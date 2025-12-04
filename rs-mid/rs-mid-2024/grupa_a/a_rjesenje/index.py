import asyncio, aiohttp, random, time
from datetime import datetime, timedelta
from VremenskaPrognoza import VremenskaPrognoza

async def simuliraj_temperaturu(broj_dana, isCool):
    rezultati = []
    for dan in range(1, broj_dana + 1):
        if isCool:
            temperatura = random.randint(0, 20)
        else:
            temperatura = random.randint(20, 40) # Temperatura ne manja od 20°C
        rezultati.append((dan, temperatura))
        await asyncio.sleep(0.1)
    return rezultati
  
async def sekvencijalno():
    start_time = time.time()
    # Pozivanje korutine dvaput
    rezultati_1 = await simuliraj_temperaturu(10, True)
    rezultati_2 = await simuliraj_temperaturu(10, False)
    
    print("Sekvencijalno:")
    print(rezultati_1)
    print(rezultati_2)
    end_time = time.time()
    razlika = end_time - start_time
    print(f"Ukupno vrijeme sekvencijalnog izvršavanja: {end_time - start_time:.2f} sekundi")
    return round(razlika, 2)

async def konkurentno():
    start_time = time.time()
    # Pozivanje korutine dvaput konkurentno

    rezultat = await asyncio.gather(simuliraj_temperaturu(10, True), simuliraj_temperaturu(10, False))
    # ili s create_task + await svaki
    
    print("Konkurentno:")
    print(rezultat)
    end_time = time.time()
    razlika = end_time - start_time
    print(f"Ukupno vrijeme konkurentnog izvršavanja: {end_time - start_time:2f} sekundi")
    return round(razlika, 2)

async def simuliraj_sljedecih_mjesec_dana(hladni_dani, instance):
  print(hladni_dani)
  for dan in hladni_dani:
    print(instance.ispis())
    novi_datum = instance.datum + timedelta(days=1)
    instance.dnevna_promjena(dan[1], novi_datum)

async def simuliraj_srpanjski_dan(json_data):
  async with aiohttp.ClientSession() as session:
    response = await session.post('http://localhost:8081/prognoza/Pula/srpanj', json=json_data)
    return await response.json()

async def main():
  prognoza_pula = VremenskaPrognoza("Pula", 12, datetime(2020, 4, 13))
  print(prognoza_pula.ispis())

  #sekvencijalno_vrijeme = await sekvencijalno()
  #konkurentno_vrijeme = await konkurentno()
  #print(f"Razlika: {sekvencijalno_vrijeme - konkurentno_vrijeme:.2f} sekundi")
  
  hladni_dani = await simuliraj_temperaturu(30, prognoza_pula)
  #await simuliraj_sljedecih_mjesec_dana(hladni_dani, prognoza_pula)


  async with aiohttp.ClientSession() as session:
    async with session.get('http://localhost:8081/prognoza/Pula') as response:
      print(await response.json())
    async with session.post('http://localhost:8081/prognoza/Pula', json={"temperatura_zraka": 10}) as response:
      print(await response.json())
  
  srpanjski_dani = await simuliraj_temperaturu(30, isCool=False)
  rezultat_srpanjske_simulacije = await asyncio.gather(*[simuliraj_srpanjski_dan({"srpanjski_dan": (dan, temperatura)}) for dan, temperatura in srpanjski_dani])
  print(rezultat_srpanjske_simulacije) # ime varijable je LOL
  
asyncio.run(main())