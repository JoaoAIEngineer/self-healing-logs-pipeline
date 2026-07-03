from pydantic import BaseModel, Field

class LLMLogSchema(BaseModel):
    request_id: str = Field(..., description="UUID único de la transacción")
    prompt: str = Field(..., min_length=1)
    response_text: str
    tokens_used: int = Field(..., gt=0, description="Tokens totales deben ser mayores a 0")