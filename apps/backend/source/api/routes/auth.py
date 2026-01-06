from azure.azure_sql_client import AzureSQLClient
from fastapi import APIRouter, Request, HTTPException
from utils.config import config
from steam.steam_client import SteamClient
from steam.models.steam_user import SteamUser
from models.user import User
from handlers.user_handler import UserHandler
from fastapi.responses import RedirectResponse
import logging
from utils.auth import create_jwt

router = APIRouter(tags=["auth"], prefix='/auth')


@router.get("/login")
async def login():
    """
    redirect to steam login
    """

    return_to = f"{config.BASE_URL}/auth/callback"
    realm = config.BASE_URL

    steam_login_url = SteamClient().get_steam_login_url(return_to, realm)
    return RedirectResponse(steam_login_url)


@router.get("/callback")
async def callback(request: Request):
    """
    Handle Steam OpenID callback
    """
    steam_client = SteamClient()

    # Validate Steam OpenID response
    steam_id = await steam_client.verify_steam_openid(dict(request.query_params))
    logging.info(f"Logged in: { steam_id }")

    if not steam_id:
        raise HTTPException(status_code=401, detail="Steam authentication failed")

    # we want to check if user exists in our db
    async with UserHandler() as user_handler:
        steam_client = SteamClient()
        user: User = await user_handler.get_user_by_steam_id(steam_id)
        if user:
            id = user.id
        else:
            user: SteamUser = await steam_client.get_steam_user(steam_id)
            if user is None:
                raise Exception("Not sure how we got here tbh, must be issue with steam")

            id = await user_handler.create_user_from_steam(user)

    token = create_jwt(steam_id, id)
    return {"access_token": token, "token_type": "bearer"}
