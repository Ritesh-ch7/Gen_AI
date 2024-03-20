from sqlalchemy.orm import Session
from src.dao.query_dao import QueryDAO
from src.dao.user_dao import UserDAO
from fastapi import HTTPException, Response
from src.services.gen_ai_service import GenAiService
from fastapi.responses import JSONResponse

class QueryService:
    def __init__(self, db: Session):
        self.query_dao = QueryDAO(db)
        self.gen_ai = GenAiService(db)
    
    async def generate_response(self, user_id, request):
        user_query = await self.fetch_query(request)

        user_query=user_query+" Dont tell me is there anything else you would like to know. Give me the (detailed + sufficient) final answer"

        session_id = await self.fetch_session_id(request)

        task_id = await self.query_dao.add_record_to_db(user_id, user_query)
        await self.query_dao.update_status(task_id, 'Inprogress')

        generated_response = await self.gen_ai.generate_response(user_query, user_id, session_id)

        await self.query_dao.update_answer_field(task_id, generated_response)
        await self.query_dao.update_status(task_id, 'Completed')
        return JSONResponse(content=generated_response)
    
    async def fetch_query(self, request):
        data = await request.json()
        return data.get('user', None)
    
    async def fetch_session_id(self, request):
        data = await request.json()
        return data.get('session_id', None)