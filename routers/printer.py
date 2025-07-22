import time
import win32print
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class PrintRequest(BaseModel):
    text: str
    printer_name: str = win32print.GetDefaultPrinter()

@router.post("/print")
def print_text(payload: PrintRequest):
    try:
        printer_name = payload.printer_name
        text_lines = payload.text.replace("\r", "").split("\n")  # clean & split

        # Open the printer
        hPrinter = win32print.OpenPrinter(printer_name)
        try:
            hJob = win32print.StartDocPrinter(hPrinter, 1, ("Receipt", None, "RAW"))
            win32print.StartPagePrinter(hPrinter)

            # Print each line with a small delay
            for line in text_lines:
                clean_line = line.strip() + "\r\n"
                win32print.WritePrinter(hPrinter, bytes(clean_line, "utf-8"))
                time.sleep(0.05)  # give printer buffer time

            # Add final feed to eject paper
            win32print.WritePrinter(hPrinter, bytes("\n\n\n", "utf-8"))

            win32print.EndPagePrinter(hPrinter)
            win32print.EndDocPrinter(hPrinter)
        finally:
            win32print.ClosePrinter(hPrinter)

        return {"status": "success", "message": "Printed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
