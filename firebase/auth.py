from fastapi import HTTPException
from firebase.config import firebase

auth = firebase.auth()

def sign_up(email, password):
    try:
        auth.create_user_with_email_and_password(email, password)
        sign_in(email, password)
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=400, detail="Failed to create user")


def sign_in(email, password):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        print(auth.get_account_info(user['idToken']))
        return user
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=400, detail="Failed to log in")