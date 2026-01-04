from handlers.user_handler import UserHandler
from constants.exceptions import UserNotFoundError
from models.jwt import AuthedJWT
from typing import Optional
from models.user import User
from fastapi import APIRouter, HTTPException, status, Depends
from utils.auth import get_current_user

router = APIRouter(tags=["user"], prefix='/user')


@router.get("/{id}", response_model_by_alias=False)
async def get_user(id, by_steam_id: Optional[bool] = False, jwt: AuthedJWT = Depends(get_current_user)) -> User:
    """
    Get user details that we want
    """

    if id == 'me':
        # this is a slighly cringe but easy way to do it
        id = jwt.steam_id if by_steam_id else jwt.id

    async with UserHandler() as uh:
        try:
            if by_steam_id:
                user = await uh.get_user_by_steam_id(id)
            else:
                user = await uh.get_user(id)
        except UserNotFoundError:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail='User not found')

    return user
