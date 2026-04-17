from fastapi import APIRouter
from app.core.agent import chat_agent

router = APIRouter(prefix="/chat", tags=["chat"])

config = {"configurable": {"thread_id": "1"}}

@router.post("/", status_code=200)
async def chat_message(message: str):
    """Chat endpoint for user messages."""
    agent = await chat_agent()

    response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": message}]},
        config
    )
    
    return {"response": response["messages"][-1].content, "user_message": message}
