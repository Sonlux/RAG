# Supabase client logic
from supabase import create_client
import os
from dotenv import load_dotenv

# Load .env from the parent directory (project root)
load_dotenv('../.env')

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase = create_client(url, key)
