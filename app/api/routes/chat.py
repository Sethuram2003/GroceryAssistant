from fastapi import APIRouter, Query
from pydantic import BaseModel
import logging

from app.core.agent import chat_agent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatResponse(BaseModel):
    response: str
    user_message: str

@router.post("/", response_model=ChatResponse, status_code=200)
async def chat_message(message: str = Query(..., description="User message")):
    """Chat endpoint for user messages."""
    try:
        agent = await chat_agent()

        response  = await agent.ainvoke(
            {"messages": [{"role": "user", "content": message}]},
            {"configurable": {"thread_id": "1"}}
        )
        
        return {
            "response": response["messages"][-1].content,
            "user_message": message
        }
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        return {
            "response": f"Error: {str(e)}",
            "user_message": message
        }

