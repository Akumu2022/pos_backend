# routers/print_linux.py
import cups
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class PrintRequest(BaseModel):
    text: str
    printer_name: str = None  # Optional

@router.post("/print")
def print_text_linux(payload: PrintRequest):
    try:
        conn = cups.Connection()
        printers = conn.getPrinters()
        printer_name = payload.printer_name or conn.getDefault()

        if printer_name not in printers:
            raise HTTPException(status_code=400, detail="Printer not found")

        # Write text to temporary file
        with open("/tmp/receipt.txt", "w") as f:
            f.write(payload.text)

        # Print file
        conn.printFile(printer_name, "/tmp/receipt.txt", "Receipt", {})
        return {"status": "success", "message": "Printed on Linux"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
