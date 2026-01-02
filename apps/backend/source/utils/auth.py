from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt import PyJWTError
from datetime import datetime, timedelta
from utils.config import config

security = HTTPBearer()


def create_jwt(steam_id: str):
    payload = {
        "sub": steam_id,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(minutes=int(config.JWT_EXPIRE_MINUTES))
    }
    return jwt.encode(payload, config.JWT_PRIVATE_KEY, algorithm='RS256')


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, config.JWT_PUBLIC_KEY, algorithms=['RS256'])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # expecting a "sub" claim
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload invalid",
        )

    return user_id
