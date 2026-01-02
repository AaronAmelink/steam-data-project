from fastapi import APIRouter, Request, HTTPException
from utils.config import config
from steam.SteamClient import SteamClient
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
    steam_data = steam_client.verify_steam_openid(dict(request.query_params))
    logging.info(steam_data)

    if not steam_data:
        raise HTTPException(status_code=401, detail="Steam authentication failed")

    token = create_jwt(steam_data)
    return {"access_token": token, "token_type": "bearer"}
