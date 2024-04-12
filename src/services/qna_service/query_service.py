from sqlalchemy.orm import Session
from src.dao.query_dao import QueryDAO
from src.dao.user_dao import UserDAO
from src.services.qna_service.gen_ai_service import GenAiService
import uuid


class QueryService:
    def __init__(self, db: Session):
        self.query_dao = QueryDAO(db)
        self.gen_ai = GenAiService(db)
    
    async def generate_response(self, request, user_id, session_id):
        user_query = await self.fetch_query(request)
        if(not session_id):
            session_id = str(uuid.uuid4())
        task_id = await self.query_dao.add_record_to_db(user_id, user_query,session_id, 'QNAService')
        await self.query_dao.update_status(task_id, 'Inprogress')

        generated_response = await self.gen_ai.generate_response(user_query, user_id, session_id)
        response = await self.query_dao.fetch_session_chat(session_id)
        await self.query_dao.update_answer_field(task_id, generated_response['bot'])
        await self.query_dao.update_status(task_id, 'Completed')
        return generated_response
        
    async def fetch_query(self, request):
        data = await request.json()
        return data.get('user', None)

    
