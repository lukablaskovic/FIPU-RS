from aiohttp import web

app = web.Application()

async def handle_euclidean(request):
  req_body = await request.json()
  
  koordinate = req_body.get("coordinates")
  
  print(koordinate)
  
  x1, y1 = koordinate[0][0], koordinate[0][1]
  x2, y2 = koordinate[1][0], koordinate[1][1]
  
  distance = round(((x2 - x1)**2 + (y2 - y1)**2)**0.5, 2)
  
  return web.json_response({"distance" : distance}, status=200)

app.router.add_post("/euclidean", handle_euclidean)

web.run_app(app, port=8091)