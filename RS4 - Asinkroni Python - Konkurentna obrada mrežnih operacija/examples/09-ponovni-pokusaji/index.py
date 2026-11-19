# Ponovi zahtjev nakon isteka vremena i pričekaj jednako dugo između pokušaja.
import asyncio


async def fetch_camera_speed(attempt):
    response_time = 0.5 if attempt <= 2 else 0.05
    await asyncio.sleep(response_time)
    return 48.2


async def main():
    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        print(f"Pokušaj {attempt}/{max_attempts}")
        try:
            speed = await asyncio.wait_for(fetch_camera_speed(attempt), timeout=0.2)
            print(f"Prosječna brzina: {speed} km/h")
            return
        except asyncio.TimeoutError:
            print("Isteklo je vrijeme za dohvat.")
            if attempt < max_attempts:
                await asyncio.sleep(1)
    print("Kamera nije odgovorila na vrijeme. Odustajemo.")


asyncio.run(main())
