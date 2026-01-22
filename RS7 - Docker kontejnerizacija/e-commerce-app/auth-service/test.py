import asyncio
import aiohttp

from get_auth0_access_token import read_token, read_scopes
from logging_setup import logging_setup

logger = logging_setup.get_logger()

async def main(): 
  try:  
    token = await read_token()
    if token is None:
      logger.error("Error: Token is None")
      return 
  except Exception as e:
    logger.error("Error: %s", e)
    return

  async with aiohttp.ClientSession() as session:
    async with session.get("https://dev-qglhozzls68dd54a.us.auth0.com/api/v2/users", headers={ 'authorization': f"Bearer {token}" }) as response:
      if response.status >= 400:
        body = await response.text()
        logger.error("Request failed (%s): %s", response.status, body)
        return

      data = await response.json()
      logger.info("Users response: %s", data)

if __name__ == "__main__":
  asyncio.run(main())

# za testiranje mikroservisa auth-service, bez poslužitelja