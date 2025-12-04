import time
import asyncio

# 3.1
def zadatak(sekunde:int)->str:
    time.sleep(sekunde)
    return f"Zadatak završen nakon {sekunde} sekundi."

def main():
    rez1, rez2, rez3 = zadatak(3), zadatak(2), zadatak(1)
    print(rez1, rez2, rez3)

# t1 = time.perf_counter()
# main()
# t2 = time.perf_counter()

# print(f"3.1 Vrijeme izvođenja programa: {(t2 - t1):.2f}")

# 3.2
async def asinkorni_zadatak(sekunde: int) -> str:
    await asyncio.sleep(sekunde)
    return f"Zadatak završen nakon {sekunde} sec."

async def main():
    taskovi = [asyncio.create_task(asinkorni_zadatak(i)) for i in range(3, 0, -1)]

    for task in taskovi:
        print(task)

    rez = await asyncio.gather(*taskovi)

    print(rez)

# t1 = time.perf_counter()
# asyncio.run(main())
# t2 = time.perf_counter()

# print(f"3.2 Vrijeme izvođenja programa: {(t2 - t1):.2f} sec.")

# 3.3
import requests

def posalji_zahtjev(url: str)-> dict:
    response = requests.get(url)
    json_odgovor = response.json()
    return json_odgovor["title"]

url = "https://jsonplaceholder.typicode.com/todos/1"
def main():
    podaci = []
    for _ in range(3):
        podaci.append(posalji_zahtjev(url))
    print(f"Podaci:\n {podaci}")

# t1 = time.perf_counter()
# main()
# t2 = time.perf_counter()

# print(f"3.3 Vrijeme izvođenja programa: {(t2 - t1):.2f} sec.")

# 3.4
import aiohttp

async def posalji_zahtjev_async(url: str, session : aiohttp.ClientSession)-> dict:
    rez = await session.get(url)
    rez_json = await rez.json()
    return rez_json["title"]

async def main():
    async with aiohttp.ClientSession() as session:
        korutine = [posalji_zahtjev_async(url, session) for _ in range(3)]    

        podaci = await asyncio.gather(*korutine)

    print(podaci)

t1 = time.perf_counter()
asyncio.run(main())
t2 = time.perf_counter()

print(f"3.4 Vrijeme izvođenja programa: {(t2 - t1):.2f} sec.")
