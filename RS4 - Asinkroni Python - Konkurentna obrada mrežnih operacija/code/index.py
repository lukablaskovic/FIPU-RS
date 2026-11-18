import time
import httpx


def send_request():
    response = httpx.get("https://catfact.ninja/fact")
    print(response.json()["fact"])


start = time.perf_counter()
for i in range(15):
    print(f"Šaljemo {i + 1}. zahtjev...")
    send_request()

end = time.perf_counter()
print(f"Izvršavanje programa traje {end - start:.2f} s.")
