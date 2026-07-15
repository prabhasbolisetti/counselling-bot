from pydantic import BaseModel


class WhatsAppMessage(BaseModel):
    phone: str
    message: str