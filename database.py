"""
Database management for Halloween Quest Bot
"""

import sqlite3
import asyncio
import aiosqlite
from datetime import datetime
from typing import Optional, Dict, Any
import json

class Database:
    def __init__(self, db_path: str = "halloween_quest.db"):
        self.db_path = db_path
    
    async def init_db(self):
        """Initialize database tables"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS family_links (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    child_session_id TEXT UNIQUE NOT NULL,
                    parent_chat_id INTEGER NOT NULL,
                    parent_username TEXT,
                    parent_first_name TEXT,
                    linked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    active BOOLEAN DEFAULT TRUE
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS photo_submissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    submission_id TEXT UNIQUE NOT NULL,
                    child_session_id TEXT NOT NULL,
                    parent_chat_id INTEGER NOT NULL,
                    task_id INTEGER NOT NULL,
                    task_name TEXT NOT NULL,
                    photo_url TEXT NOT NULL,
                    photo_path TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',  -- pending, approved, rejected
                    parent_comment TEXT,
                    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    reviewed_at TIMESTAMP,
                    FOREIGN KEY (child_session_id) REFERENCES family_links (child_session_id)
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS bot_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER NOT NULL,
                    message_id INTEGER NOT NULL,
                    submission_id TEXT,
                    message_type TEXT,  -- link_request, photo_review, etc.
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            await db.commit()
    
    async def create_family_link(self, child_session_id: str, parent_chat_id: int, 
                               parent_username: str = None, parent_first_name: str = None) -> bool:
        """Create a link between child and parent"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO family_links 
                    (child_session_id, parent_chat_id, parent_username, parent_first_name)
                    VALUES (?, ?, ?, ?)
                """, (child_session_id, parent_chat_id, parent_username, parent_first_name))
                await db.commit()
                return True
        except Exception as e:
            print(f"Error creating family link: {e}")
            return False
    
    async def get_parent_by_session(self, child_session_id: str) -> Optional[Dict[str, Any]]:
        """Get parent info by child session ID"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT * FROM family_links 
                WHERE child_session_id = ? AND active = TRUE
            """, (child_session_id,))
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    async def check_family_link(self, child_session_id: str) -> bool:
        """Check if family link exists and is active"""
        parent = await self.get_parent_by_session(child_session_id)
        return parent is not None
    
    async def submit_photo(self, submission_id: str, child_session_id: str, 
                          task_id: int, task_name: str, photo_url: str, photo_path: str) -> bool:
        """Submit a photo for parent review"""
        try:
            parent = await self.get_parent_by_session(child_session_id)
            if not parent:
                return False
                
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO photo_submissions 
                    (submission_id, child_session_id, parent_chat_id, task_id, task_name, photo_url, photo_path)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (submission_id, child_session_id, parent["parent_chat_id"], task_id, task_name, photo_url, photo_path))
                await db.commit()
                return True
        except Exception as e:
            print(f"Error submitting photo: {e}")
            return False
    
    async def get_photo_submission(self, submission_id: str) -> Optional[Dict[str, Any]]:
        """Get photo submission by ID"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT * FROM photo_submissions WHERE submission_id = ?
            """, (submission_id,))
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    async def update_photo_status(self, submission_id: str, status: str, parent_comment: str = None) -> bool:
        """Update photo submission status"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    UPDATE photo_submissions 
                    SET status = ?, parent_comment = ?, reviewed_at = CURRENT_TIMESTAMP
                    WHERE submission_id = ?
                """, (status, parent_comment, submission_id))
                await db.commit()
                return True
        except Exception as e:
            print(f"Error updating photo status: {e}")
            return False
    
    async def save_bot_message(self, chat_id: int, message_id: int, 
                              submission_id: str = None, message_type: str = None):
        """Save bot message info for later reference"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO bot_messages 
                (chat_id, message_id, submission_id, message_type)
                VALUES (?, ?, ?, ?)
            """, (chat_id, message_id, submission_id, message_type))
            await db.commit()

# Global database instance
db = Database()
