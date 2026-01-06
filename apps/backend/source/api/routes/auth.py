from azure.azure_sql_client import AzureSQLClient
from fastapi import APIRouter, Request, HTTPException
from utils.config import config
from steam.steam_client import SteamClient
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
    async with AzureSQLClient() as sql:
        query = f"""
        SELECT
            id
        FROM user_accounts
        WHERE
            steam_id = {steam_id}
        """

        id = await sql.query_one(query)
        if id:
            id = id['id']
        else:
            steam = SteamClient()
            user = await steam.get_steam_user(steam_id)
            if user is None:
                raise Exception("Not sure how we got here tbh, must be issue with steam")

            logging.info(user)

            insert = f"""
            INSERT INTO user_accounts
                (
                    steam_id,
                    name
                )
            OUTPUT INSERTED.id
            VALUES
                (
                    {steam_id},
                    '{user.name}'
                )
            """
            res = await sql.query_one(insert)
            logging.info(res)

            if not res['id']:
                raise Exception("could not insert new user")

            id = res['id']

    token = create_jwt(steam_id, id)
    return {"access_token": token, "token_type": "bearer"}
