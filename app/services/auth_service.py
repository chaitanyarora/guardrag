from typing import Dict

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials


security = HTTPBasic()


# Temporary user database.
# We will replace this with a proper authentication mechanism later.
users_db: Dict[str, Dict[str, str]] = {
    "Tony": {"password": "password123", "role": "engineering"},
    "Bruce": {"password": "securepass", "role": "marketing"},
    "Sam": {"password": "financepass", "role": "finance"},
    "Peter": {"password": "pete123", "role": "engineering"},
    "Sid": {"password": "sidpass123", "role": "marketing"},
    "Natasha": {"password": "hrpass123", "role": "hr"},
}


def authenticate(
    credentials: HTTPBasicCredentials = Depends(security),
):
    username = credentials.username
    password = credentials.password

    user = users_db.get(username)

    if not user or user["password"] != password:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )

    return {
        "username": username,
        "role": user["role"],
    }