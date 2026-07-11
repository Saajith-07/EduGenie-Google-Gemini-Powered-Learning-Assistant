import uuid
import json
import logging
import google.generativeai as genai
from fastapi import APIRouter, HTTPException
from models.schemas import ChatRequest, ChatResponse
from utils.db_manager import log_query, log_ai_response
from utils.gemini_service import is_gemini_active, get_mock_chat_response, best_model_name

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter()

def answer_question_with_gemini(question: str) -> str:
    """Core educational QnA logic using Gemini."""
    try:
        if not is_gemini_active:
            # Fallback for Demo mode
            mock_data = get_mock_chat_response(question)
            return mock_data.explanation
            
        model = genai.GenerativeModel(model_name=best_model_name)
        response = model.generate_content(question)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Error in answer_question_with_gemini: {str(e)}")
        return f"⚠️ Error in QnA: {e}"

@router.post("/ask", response_model=ChatResponse)
async def ask_question(request: ChatRequest):
    """Endpoint to answer educational questions with detailed responses."""
    try:
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty.")
        
        # 1. Log query
        query_id = uuid.uuid4().hex
        log_query(query_id, "qa", request.question)
        
        # 2. Get response from core logic
        explanation_text = answer_question_with_gemini(request.question)
        
        # Format response to match ChatResponse schema
        if not is_gemini_active:
            # Return full mock response schema directly for high fidelity
            response = get_mock_chat_response(request.question)
        else:
            # Construct schema from raw Gemini output
            response = ChatResponse(
                answer=f"Answer for: {request.question}",
                explanation=explanation_text,
                example="Refer to the detailed explanation block above.",
                key_points=["Detailed concept analysis", "Context-aware response from Gemini 1.5 Pro"]
            )
        
        # 3. Log response
        response_id = uuid.uuid4().hex
        response_text = json.dumps(response.model_dump())
        log_ai_response(response_id, query_id, response_text, "Gemini")
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
