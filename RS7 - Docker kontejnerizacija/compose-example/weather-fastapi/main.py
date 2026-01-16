from fastapi import FastAPI, HTTPException, status
from models import Vrijeme
import aiohttp
import xml.etree.ElementTree as ET

app = FastAPI()

# main.py
@app.get("/vrijeme", response_model = list[Vrijeme])
async def get_vrijeme():
  """
  Dohvaća podatke o vremenu sa DHMZ API-ja, ali u JSON-u!  

  Podaci dostupni na https://prognoza.hr/prognoza_sutra.xml
  """
  url = "https://prognoza.hr/prognoza_sutra.xml" 

  try:
    async with aiohttp.ClientSession() as session:
      response = await session.get(url)
      if response.status != 200: # u slučaju greške
        raise HTTPException(status_code=response.status, detail="Greška u dohvaćanju XML podataka s DHMZ API-ja")
      xml_data = await response.text()
  except Exception as e: # Uhvati sve greške ako dođe do problema u slanju zahtjeva
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Greška u slanju HTML zahtjeva na DHMZ API")

  root = ET.fromstring(xml_data)
  stations = root.findall(".//station")
  weather_list = []
  
  for station in stations:
    mjesto = station.attrib.get("name")
    temperatura_min = int(station.find("./param[@name='Tmn']").attrib.get("value"))
    temperatura_max = int(station.find("./param[@name='Tmx']").attrib.get("value"))
    vjetar = int(station.find("./param[@name='wind']").attrib.get("value"))
    weather_list.append(Vrijeme(
                    mjesto=mjesto,
                    temperatura_min=temperatura_min,
                    temperatura_max=temperatura_max,
                    vjetar=vjetar
                ))
  return weather_list

@app.get("/regije")
async def get_regije():
  async with aiohttp.ClientSession() as session:
    response = await session.get("http://aiohttp-regije:4000/regije") # koristimo naziv kontejnera kao domenu
    regije = await response.json()
    return regije