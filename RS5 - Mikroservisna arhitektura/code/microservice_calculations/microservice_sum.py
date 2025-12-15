from aiohttp import web

app = web.Application()

async def zbroj_brojeva_lista(request):
  tijelo_zahtjeva = await request.json()
  
  brojevi = tijelo_zahtjeva.get("brojevi")
  
  zbroj = sum(brojevi)
  print({"zbroj" : zbroj})
  return web.json_response({"zbroj" : zbroj})

app.router.add_post("/zbroj", zbroj_brojeva_lista)

web.run_app(app, host='localhost', port=8081)


[1, 2, 3, 4, 5]
# prvi vraca zbroj

# ([1, 2, 3, 4, 5], zbroj)

# [1/zbroj, 2/zbroj, 3/zbroj]