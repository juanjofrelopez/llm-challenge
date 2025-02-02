from pydantic import BaseModel
from datetime import datetime, time

class CsvEntry(BaseModel):
    date: datetime
    week_day: str
    hour: time
    ticket_number: str
    waiter: int
    product_name: str
    quantity: float
    unitary_price: float
    total: float

class PromptRequest(BaseModel):
    prompt: str