from aiohttp import web
from datetime import datetime, timedelta
from VremenskaPrognoza import VremenskaPrognoza

app = web.Application()

# dummy
prognoze = {
    "Pula": VremenskaPrognoza("Pula", 12, datetime(2024, 12, 18)),
    "Zagreb": VremenskaPrognoza("Zagreb", 15, datetime(2024, 12, 18)),
    "Split": VremenskaPrognoza("Split", 18, datetime(2024, 12, 18)),
}

async def handle_get_prognoza(request):
    grad = request.match_info.get('grad')
    prognoza = prognoze.get(grad)
    return web.json_response({"prognoza" : prognoza.ispis()})

async def handle_post_prognoza(request):
  grad = request.match_info.get('grad')
  if grad not in prognoze:
    return web.json_response({"greska" : "Grad nije pronađen"}, status=404)
  data = await request.json()
  nova_temperatura = data.get('temperatura_zraka')
  prognoza = prognoze[grad]
  prognoza.dnevna_promjena(nova_temperatura, datetime.now())
  print(prognoza.ispis())
  return web.json_response({"message" : f"Prognoza postavljena za grad {grad} za današnji datum."})

async def simulate_srpanj(request):
  
  grad = request.match_info.get('grad')
  data = await request.json()
  
  dan = data.get('srpanjski_dan')[0]
  temperatura = data.get('srpanjski_dan')[1]
  
  if grad not in prognoze:
    return web.json_response({"greska" : "Grad nije pronađen"}, status=404)
  
  if dan < 1 or dan > 31:
    return web.json_response({"greska" : "Dan nije ispravan"}, status=400)
  
  instanca = prognoze.get(grad)
  
  print(instanca.ispis())
  instanca.dnevna_promjena(temperatura, datetime(2025, 7, dan))

  return web.json_response({"dan_temp" : instanca.ispis()}, status=200)


app.router.add_get('/prognoza/{grad}', handle_get_prognoza)
app.router.add_post('/prognoza/{grad}', handle_post_prognoza)
app.router.add_post('/prognoza/{grad}/srpanj', simulate_srpanj)

web.run_app(app, port=8081)