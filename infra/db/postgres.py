import os
from dotenv import load_dotenv
from supabase import create_client, Client
from typing import Optional
import ssl
import certifi

load_dotenv()

class PostgresConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PostgresConnection, cls).__new__(cls)
            cls._instance._initialize_client()
        return cls._instance

    def _initialize_client(self):
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')
        
        if not url or not key:
            raise ValueError("Missing Supabase credentials. Please check your .env file")
            
        # Đảm bảo URL có định dạng đúng
        if not url.startswith('https://'):
            url = f'https://{url}'
            
        # Nếu URL chứa 'db.', thay thế bằng project URL
        if 'db.' in url:
            project_id = url.split('db.')[1].split('.')[0]
            url = f'https://{project_id}.supabase.co'
            
        try:
            # Tạo SSL context với certifi
            ssl_context = ssl.create_default_context(cafile=certifi.where())
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

            # Tạo client với SSL context
            self.supabase: Client = create_client(url, key)
            
            # Test connection
            self.supabase.table('discord_server').select('count').limit(1).execute()
            print("Successfully connected to Supabase!")
        except Exception as e:
            raise Exception(f"Failed to connect to Supabase: {str(e)}")

    def get_table(self, table_name: str):
        return self.supabase.table(table_name)

# Singleton instance
postgres = PostgresConnection() 