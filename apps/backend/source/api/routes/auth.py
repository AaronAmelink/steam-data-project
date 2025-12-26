from fastapi import APIRouter
from utils.config import config
from steam.SteamClient import SteamClient
from fastapi.responses import RedirectResponse

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
