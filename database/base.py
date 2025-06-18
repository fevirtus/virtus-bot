from supabase import create_client, Client
import os
from dotenv import load_dotenv
from infra.db import PostgresConnection

load_dotenv()

class Database:
    def __init__(self):
        uri: str = os.getenv('SUPABASE_URI')
        if not uri:
            raise ValueError("SUPABASE_URI environment variable is not set")
            
        # Parse URI to get URL and key
        # Format: postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
        parts = uri.split('@')
        if len(parts) != 2:
            raise ValueError("Invalid SUPABASE_URI format")
            
        # Extract project reference from the host
        host = parts[1].split(':')[0]
        project_ref = host.split('.')[1]
        
        # Construct Supabase URL and key
        url = f"https://{project_ref}.supabase.co"
        key = os.getenv('SUPABASE_KEY')  # Still need the anon key for API access
        
        if not key:
            raise ValueError("SUPABASE_KEY environment variable is not set")
            
        self.supabase: Client = create_client(url, key) 

class BaseRepository:
    def __init__(self):
        self.db = PostgresConnection() 