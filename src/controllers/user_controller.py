from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.services.user_service import UserService

class UserController:
    def __init__(self, db : Session):
        self.user_service = UserService(db)
    
    async def fetch_previous_chat(self, session_id):
        return await self.user_service.fetch_previous_chat(session_id)