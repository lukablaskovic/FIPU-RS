# Ograniči obradu na dvije kamere istodobno i prati kada svaka počinje i završava.
import asyncio


async def process_camera(camera_id, semaphore):
    async with semaphore:
        print(f"Kamera {camera_id}: početak obrade.")
        await asyncio.sleep(1)
        print(f"Kamera {camera_id}: kraj obrade.")


async def main():
    semaphore = asyncio.Semaphore(2)
    dohvati = [process_camera(camera_id, semaphore) for camera_id in range(1, 6)]
    await asyncio.gather(*dohvati)


asyncio.run(main())
