from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def list_purchases():
    return {"message": "List of purchases"}
