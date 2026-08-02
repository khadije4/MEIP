from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.assistant.engine import answer_question
from app.database import get_db
from app.schemas.assistant import AssistantAnswer, AssistantQuery

router = APIRouter(prefix="/api/assistant", tags=["assistant"])

@router.post("/query", response_model=AssistantAnswer)
def query(body: AssistantQuery, db: Session = Depends(get_db)) -> AssistantAnswer:
    return answer_question(db, body.question, body.language, body.last_indicator_codes, body.last_year)
