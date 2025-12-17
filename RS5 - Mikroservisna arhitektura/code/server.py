from aiohttp import web
import json

app = web.Application()


data = {"ime": "Ivo", "prezime": "Ivić", "godine": 25}

print(json.dumps(data))


def handler(request):
    print(request.method)
    print(request.headers)
    print(request.path)
    # return web.Response(text="Pozdrav Raspodijeljeni sustavi")
    return web.Response(text=json.dumps(data), content_type="application/json")
    # return web.json_response(data)


app.router.add_get("/", handler)

web.run_app(app, host="localhost", port=3030)
