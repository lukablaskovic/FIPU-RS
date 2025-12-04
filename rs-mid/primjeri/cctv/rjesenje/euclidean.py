from aiohttp import web

app = web.Application()

async def handle_euclidean_distance(request):
  data = await request.json()
  coordinates = data.get("coordinates")
  print(f"Zaprimljen zahtjev za koordinate: {coordinates}")
  
  x1, y1 = coordinates[0]
  x2, y2 = coordinates[1]
  
  distance = round(((x2 - x1)**2 + (y2 - y1)**2)**0.5, 2)
  
  return web.json_response({"distance": distance})

app.router.add_post('/euclidean', handle_euclidean_distance)

if __name__ == "__main__":
  web.run_app(app, port=8091)
  