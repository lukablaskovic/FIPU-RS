# Prema uputama na manage.auth0.com/dashboard
# 1. Obtaining an Access Token by Calling the Token Endpoint

import argparse
import json
import os
import asyncio, aiohttp
from dotenv import load_dotenv  # pyright: ignore[reportMissingImports]
from logging_setup import logging_setup

load_dotenv()

logger = logging_setup.get_logger()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUDIENCE = os.getenv("AUDIENCE")

parser = argparse.ArgumentParser(description="Get Auth0 access token")
parser.add_argument("--save", action="store_true", help="Save the access token to a file")

async def get_auth0_access_token_corutine() -> str:
  try:
    async with aiohttp.ClientSession() as session:
        async with session.post(f"https://{AUTH0_DOMAIN}/oauth/token", json={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "audience": AUDIENCE,
            "grant_type": "client_credentials"
        }) as response:
            data = await response.json()
            if parser.parse_args().save:
              try:
                with open("auth0_access_token.json", "w") as f:
                    json.dump(data, f, indent=4)
                    logger.info("Auth0 access token saved to file: %s", "auth0_access_token.json")
              except Exception as e:
                logger.error("Error saving auth0 access token to file: %s", e)
            else:
                logger.info("Auth0 access token: %s", data)
            return data["access_token"]
  except Exception as e:
    logger.error("Error getting auth0 access token: %s", e)
    return None

async def read_token() -> str:
  try:
    with open("auth0_access_token.json", "r") as f:
      data = json.load(f)
      return data["access_token"]
  except Exception as e:
    logger.error("Error reading auth0 access token from file: %s", e)
    return None

async def read_scopes() -> list[str]:
  try:
    with open("auth0_access_token.json", "r") as f:
      data = json.load(f)
      return data["scope"]
  except Exception as e:
    logger.error("Error reading auth0 scopes from file: %s", e)
    return None


# Za dobivanje tokena na service-strani
if __name__ == "__main__":
    asyncio.run(get_auth0_access_token_corutine())
