from fastapi import APIRouter
from app.schemas import GenerateRequest, FeedbackRequest
from app.ai.architecture_assistant import generate_architecture, review_architecture
import json

router = APIRouter()

@router.post("/generate")
def generate(request: GenerateRequest):
    result = generate_architecture(request.prompt)
    if isinstance(result, str):
        return json.loads(result)
    return result

@router.post("/feedback")
def feedback(request: FeedbackRequest):
    return {"suggestions": review_architecture(request.model)}
