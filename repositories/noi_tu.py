from typing import List, Optional
from models.noi_tu import DiscordNoiTu
from infra.db import postgres
from datetime import datetime
import random

class NoiTuRepository:
    def __init__(self):
        self.table = postgres.get_table('dictionary_vietnamese_two_words')

    async def is_exist(self, word: str) -> bool:
        """Kiểm tra xem từ có tồn tại trong bảng không"""
        try:
            word = word.strip()
            response = self.table.select('*').eq('word', word).execute()
            return len(response.data) > 0
        except Exception as e:
            print(f"Error checking if word exists: {e}")
            return False
        
    async def add(self, word: str, meaning: Optional[str] = None) -> bool:
        """Thêm từ vào bảng"""
        try:
            response = self.table.insert({
                'word': word,
                'meaning': meaning
            }).execute()
            return response.data is not None
        except Exception as e:
            print(f"Error adding word: {e}")
            return False
        
    async def remove(self, word: str) -> bool:
        """Xóa từ khỏi bảng"""
        try:
            response = self.table.delete().eq('word', word).execute()
            return response.data is not None
        except Exception as e:
            print(f"Error removing word: {e}")
            return False
    
    async def get_random_word(self) -> Optional[str]:
        """Lấy một từ ngẫu nhiên từ bảng"""
        try:
            response = self.table.select('word').execute()
            if response.data and len(response.data) > 0:
                # Lọc từ có đúng 2 từ ghép, mỗi từ chỉ gồm chữ cái
                words = []
                for item in response.data:
                    word = item['word'].strip()
                    parts = word.split()
                    if len(parts) == 2 and all(part.isalpha() for part in parts):
                        words.append(word)
                if words:
                    return random.choice(words)
            return None
        except Exception as e:
            print(f"Error getting random word: {e}")
            return None
    
    async def get_all_words(self) -> List[str]:
        """Lấy tất cả từ trong bảng"""
        try:
            response = self.table.select('word').execute()
            if response.data:
                # Lọc từ có đúng 2 từ ghép, mỗi từ chỉ gồm chữ cái
                words = []
                for item in response.data:
                    word = item['word'].strip()
                    parts = word.split()
                    if len(parts) == 2 and all(part.isalpha() for part in parts):
                        words.append(word)
                return words
            return []
        except Exception as e:
            print(f"Error getting all words: {e}")
            return []
    
    async def is_valid_word(self, word: str) -> bool:
        """Kiểm tra từ có hợp lệ không (2 từ ghép, mỗi từ chỉ gồm chữ cái)"""
        word = word.strip()
        parts = word.split()
        if len(parts) != 2:
            return False
        return all(part.isalpha() for part in parts)
        