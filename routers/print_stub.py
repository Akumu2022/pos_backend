# routers/print_stub.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class PrintRequest(BaseModel):
    text: str
    printer_name: str

@router.post("/print")
def print_text_stub(payload: PrintRequest):
    raise HTTPException(status_code=501, detail="🖨️ Printing is not supported on this server OS")
