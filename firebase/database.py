from fastapi import HTTPException
from firebase.config import firebase

db = firebase.database()

def write_data(data):
    try:
        db.push(data)
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=400, detail="Failed to write data")