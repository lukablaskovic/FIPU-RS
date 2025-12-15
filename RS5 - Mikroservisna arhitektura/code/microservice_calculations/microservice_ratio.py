from aiohttp import web

app = web.Application()

async def izracun_omjera_elemenata(request):
  tijelo_zahtjeva = await request.json()
  
  brojevi = tijelo_zahtjeva.get("brojevi")
  zbroj = tijelo_zahtjeva.get("zbroj")
  
  lista_omjera = [round(broj/zbroj, 2) for broj in brojevi]
  
  print({"lista_omjera" : lista_omjera})
  return web.json_response({"lista_omjera" : lista_omjera})

app.router.add_post("/ratio", izracun_omjera_elemenata)

web.run_app(app, host='localhost', port=8082)