# Authentication endpoints
from fastapi import APIRouter, HTTPException, Depends, Cookie, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import uuid
from datetime import datetime, timedelta
from typing import Optional
from db.supabase_client import supabase

router = APIRouter()

class User(BaseModel):
    email: str
    name: str
    avatar: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserRegister(BaseModel):
    email: str
    name: str
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    avatar: Optional[str] = None

@router.post("/auth/login")
def login(user_data: UserLogin, response: Response):
    """Login a user and create a session"""
    # Query the user from Supabase
    user_result = supabase.table("users").select("*").eq("email", user_data.email).execute()
    
    if not user_result.data:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    user = user_result.data[0]
    
    # In production, you should use proper password hashing and verification
    if user["password"] != user_data.password:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create a session
    session_id = str(uuid.uuid4())
    expires_at = datetime.now() + timedelta(days=7)
    
    # Store session in Supabase
    supabase.table("sessions").insert({
        "session_id": session_id,
        "user_id": user["id"],
        "expires_at": expires_at.isoformat()
    }).execute()
    
    # Set session cookie
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        expires=expires_at.timestamp(),
        secure=False,  # Set to True in production with HTTPS
        samesite="lax"
    )
    
    return {
        "status": "success",
        "user": {
            "email": user["email"],
            "name": user["name"],
            "avatar": user["avatar"]
        }
    }

@router.post("/auth/register")
def register(user_data: UserRegister, response: Response):
    """Register a new user"""
    # Check if user already exists
    user_exists = supabase.table("users").select("email").eq("email", user_data.email).execute()
    
    if user_exists.data:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user in Supabase
    user_result = supabase.table("users").insert({
        "email": user_data.email,
        "name": user_data.name,
        "password": user_data.password,  # In production, hash the password
        "avatar": None
    }).execute()
    
    if not user_result.data:
        raise HTTPException(status_code=500, detail="Failed to create user")
    
    new_user = user_result.data[0]
    
    # Create a session
    session_id = str(uuid.uuid4())
    expires_at = datetime.now() + timedelta(days=7)
    
    # Store session in Supabase
    supabase.table("sessions").insert({
        "session_id": session_id,
        "user_id": new_user["id"],
        "expires_at": expires_at.isoformat()
    }).execute()
    
    # Set session cookie
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        expires=expires_at.timestamp(),
        secure=False,  # Set to True in production with HTTPS
        samesite="lax"
    )
    
    return {
        "status": "success",
        "user": {
            "email": new_user["email"],
            "name": new_user["name"],
            "avatar": new_user["avatar"]
        }
    }

@router.post("/auth/logout")
def logout(response: Response, session_id: Optional[str] = Cookie(None)):
    """Logout a user by clearing the session"""
    if session_id:
        # Delete session from database
        supabase.table("sessions").delete().eq("session_id", session_id).execute()
    
    response.delete_cookie(key="session_id")
    return {"status": "success"}

@router.get("/auth/me")
def get_current_user(session_id: Optional[str] = Cookie(None)):
    """Get the current logged-in user"""
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Get session from database
    session_result = supabase.table("sessions").select("*").eq("session_id", session_id).execute()
    
    if not session_result.data:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    session = session_result.data[0]
    
    # Check if session is expired
    expires_at = datetime.fromisoformat(session["expires_at"])
    if expires_at < datetime.now():
        # Delete expired session
        supabase.table("sessions").delete().eq("session_id", session_id).execute()
        raise HTTPException(status_code=401, detail="Session expired")
    
    # Get user from database
    user_result = supabase.table("users").select("*").eq("id", session["user_id"]).execute()
    
    if not user_result.data:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = user_result.data[0]
    
    return {
        "email": user["email"],
        "name": user["name"],
        "avatar": user["avatar"]
    }

@router.put("/auth/me")
def update_user(user_data: UserUpdate, session_id: Optional[str] = Cookie(None)):
    """Update the current user's profile"""
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Get session from database
    session_result = supabase.table("sessions").select("*").eq("session_id", session_id).execute()
    
    if not session_result.data:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    session = session_result.data[0]
    
    # Check if session is expired
    expires_at = datetime.fromisoformat(session["expires_at"])
    if expires_at < datetime.now():
        # Delete expired session
        supabase.table("sessions").delete().eq("session_id", session_id).execute()
        raise HTTPException(status_code=401, detail="Session expired")
    
    # Prepare update data
    update_data = {}
    if user_data.name is not None:
        update_data["name"] = user_data.name
    if user_data.avatar is not None:
        update_data["avatar"] = user_data.avatar
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")
    
    # Update user in database
    user_result = supabase.table("users").update(update_data).eq("id", session["user_id"]).execute()
    
    if not user_result.data:
        raise HTTPException(status_code=404, detail="User not found")
    
    updated_user = user_result.data[0]
    
    return {
        "status": "success",
        "user": {
            "email": updated_user["email"],
            "name": updated_user["name"],
            "avatar": updated_user["avatar"]
        }
    }

# Dependency to get the current user
async def get_current_user_dependency(session_id: Optional[str] = Cookie(None)):
    """Dependency to get the current user for protected routes"""
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Get session from database
    session_result = supabase.table("sessions").select("*").eq("session_id", session_id).execute()
    
    if not session_result.data:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    session = session_result.data[0]
    
    # Check if session is expired
    expires_at = datetime.fromisoformat(session["expires_at"])
    if expires_at < datetime.now():
        # Delete expired session
        supabase.table("sessions").delete().eq("session_id", session_id).execute()
        raise HTTPException(status_code=401, detail="Session expired")
    
    # Get user from database
    user_result = supabase.table("users").select("*").eq("id", session["user_id"]).execute()
    
    if not user_result.data:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user_result.data[0]