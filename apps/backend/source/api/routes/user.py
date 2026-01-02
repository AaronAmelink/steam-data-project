from fastapi import APIRouter, Request, HTTPException, status, Depends
from utils.config import config
from steam.SteamClient import SteamClient
from fastapi.responses import RedirectResponse
import logging
from utils.auth import get_current_user

router = APIRouter(tags=["user"], prefix='/user')


@router.get("/{id}/ping")
async def ping(id, jwt_id: dict = Depends(get_current_user)):
    """
    ensure user is valid login
    """

    logging.info(jwt_id)
    if id != jwt_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid Request")

    return id

@router.get("/{id}")
async def get_user(id, jwt_id: dict = Depends(get_current_user)):
    """
    Get current user details from steam
    """
