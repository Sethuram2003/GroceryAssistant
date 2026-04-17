from fastapi import APIRouter

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", status_code=200)
def chat_message(message: str):
    """Chat endpoint for user messages."""
    return {"response": "Chat functionality coming soon", "user_message": message}
