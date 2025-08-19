import React, {
  createContext,
  useState,
  useContext,
  useEffect,
  ReactNode,
} from "react";

const API_BASE = "http://localhost:8000";

interface User {
  email: string;
  name: string;
  avatar: string | null;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, name: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  updateProfile: (name?: string, avatar?: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Check if user is already logged in
    const checkAuth = async () => {
      try {
        const res = await fetch(`${API_BASE}/auth/me`, {
          credentials: "include", // Include cookies
        });
        if (res.ok) {
          const userData = await res.json();
          setUser(userData);
        }
      } catch (error) {
        console.error("Auth check failed:", error);
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = async (email: string, password: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
        credentials: "include", // Include cookies
      });

      if (!res.ok) {
        const errorText = await res.text();
        let errorMessage = "Login failed";

        try {
          const errorData = JSON.parse(errorText);
          errorMessage = errorData.detail || "Login failed";
        } catch (e) {
          console.error("Failed to parse error response:", errorText);
          errorMessage = `Login failed: ${res.status} ${res.statusText}`;
        }

        throw new Error(errorMessage);
      }

      const data = await res.json();
      setUser(data.user);
    } catch (error) {
      console.error("Login error:", error);
      setError(error instanceof Error ? error.message : "Login failed");
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const register = async (email: string, name: string, password: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, name, password }),
        credentials: "include", // Include cookies
      });

      if (!res.ok) {
        const errorText = await res.text();
        let errorMessage = "Registration failed";

        try {
          const errorData = JSON.parse(errorText);
          errorMessage = errorData.detail || "Registration failed";
        } catch (e) {
          console.error("Failed to parse error response:", errorText);
          errorMessage = `Registration failed: ${res.status} ${res.statusText}`;
        }

        throw new Error(errorMessage);
      }

      const data = await res.json();
      setUser(data.user);
    } catch (error) {
      console.error("Registration error:", error);
      setError(error instanceof Error ? error.message : "Registration failed");
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      await fetch(`${API_BASE}/auth/logout`, {
        method: "POST",
        credentials: "include", // Include cookies
      });
      setUser(null);
    } catch (error) {
      console.error("Logout error:", error);
    }
  };

  const updateProfile = async (name?: string, avatar?: string) => {
    if (!user) return;

    setLoading(true);
    setError(null);
    try {
      const updateData: { name?: string; avatar?: string } = {};
      if (name !== undefined) updateData.name = name;
      if (avatar !== undefined) updateData.avatar = avatar;

      const res = await fetch(`${API_BASE}/auth/me`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updateData),
        credentials: "include", // Include cookies
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Profile update failed");
      }

      const data = await res.json();
      setUser(data.user);
    } catch (error) {
      console.error("Profile update error:", error);
      setError(
        error instanceof Error ? error.message : "Profile update failed"
      );
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const value = {
    user,
    loading,
    error,
    login,
    register,
    logout,
    updateProfile,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
