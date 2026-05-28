from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class EmailRequest(BaseModel):
    """Modelo para solicitação de processamento de e-mail."""
    subject: str = Field(..., example="Problema com pagamento")
    body: str = Field(..., example="Paguei ontem e ainda não confirmou.")
    sender: Optional[str] = Field("api-user@example.com", example="cliente@exemplo.com")

class EmailResponse(BaseModel):
    """Modelo para resposta de e-mail processado."""
    id: str
    sender: str
    subject: str
    category: str
    urgent: bool
    summary: str
    recommended_action: str
    processed_at: datetime

    class Config:
        from_attributes = True
