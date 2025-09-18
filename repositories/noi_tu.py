from typing import List, Optional
from datetime import datetime
import random
from sqlalchemy import select, delete

from models.noi_tu import DiscordNoiTu
from infra.db import postgres

class NoiTuRepository:
    def __init__(self):
        self.Session = postgres.get_sessionmaker()

    async def is_exist(self, word: str) -> bool:
        """Kiểm tra xem từ có tồn tại trong bảng không"""
        try:
            word = word.strip()
            async with self.Session() as session:
                stmt = select(DiscordNoiTu).where(DiscordNoiTu.word == word).limit(1)
                result = await session.execute(stmt)
                return result.scalar_one_or_none() is not None
        except Exception as e:
            print(f"Error checking if word exists: {e}")
            return False
        
    async def add(self, word: str) -> bool:
        """Thêm từ vào bảng"""
        try:
            # Kiểm tra từ đã tồn tại chưa trước khi thêm
            if await self.is_exist(word):
                print(f"Word '{word}' already exists")
                return False
                
            async with self.Session() as session:
                # Lấy ID cao nhất hiện tại và tạo ID mới
                stmt = select(DiscordNoiTu.id).order_by(DiscordNoiTu.id.desc()).limit(1)
                result = await session.execute(stmt)
                max_id = result.scalar_one_or_none()
                next_id = (max_id + 1) if max_id is not None else 1
                
                # Tạo object với ID cụ thể
                noi_tu = DiscordNoiTu(id=next_id, word=word)
                session.add(noi_tu)
                await session.commit()
                return True
        except Exception as e:
            print(f"Error adding word: {e}")
            return False
        
    async def remove(self, word: str) -> bool:
        """Xóa từ khỏi bảng"""
        try:
            async with self.Session() as session:
                stmt = delete(DiscordNoiTu).where(DiscordNoiTu.word == word)
                await session.execute(stmt)
                await session.commit()
                return True
        except Exception as e:
            print(f"Error removing word: {e}")
            return False
    
    async def get_random_word(self) -> Optional[str]:
        """Lấy một từ ngẫu nhiên từ bảng"""
        try:
            async with self.Session() as session:
                stmt = select(DiscordNoiTu.word)
                result = await session.execute(stmt)
                words: List[str] = []
                for row in result.scalars():
                    word = row.strip()
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
            async with self.Session() as session:
                stmt = select(DiscordNoiTu.word)
                result = await session.execute(stmt)
                words: List[str] = []
                for row in result.scalars():
                    word = row.strip()
                    parts = word.split()
                    if len(parts) == 2 and all(part.isalpha() for part in parts):
                        words.append(word)
                return words
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
        