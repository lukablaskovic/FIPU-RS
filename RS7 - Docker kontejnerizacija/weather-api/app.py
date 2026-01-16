from fastapi import FastAPI, HTTPException
from models import Vrijeme
import aiohttp
from fastapi import status
import xml.etree.ElementTree as ET

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello, weather API!"}


@app.get("/vrijeme", response_model=list[Vrijeme])
async def get_vrijeme():
    """
    Dohvaća podatke o vremenu sa DHMZ API-ja, ali u JSON-u!

    Podaci dostupni na https://prognoza.hr/prognoza_sutra.xml
    """
    url = "https://prognoza.hr/prognoza_sutra.xml"

    try:
        async with aiohttp.ClientSession() as session:
            response = await session.get(url)
            if response.status != 200:  # u slučaju greške
                raise HTTPException(
                    status_code=response.status,
                    detail="Greška u dohvaćanju XML podataka s DHMZ API-ja",
                )
            xml_data = await response.text()
    except Exception as e:  # Uhvati sve greške ako dođe do problema u slanju zahtjeva
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Greška u slanju HTML zahtjeva na DHMZ API",
        )
