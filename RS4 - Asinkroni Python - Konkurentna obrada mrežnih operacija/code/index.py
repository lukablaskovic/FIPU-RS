import asyncio
import random
import time


async def process_camera(camera_id, semaphore):
    async with semaphore:
        print(f"Kamera {camera_id}: započinje obradu")

        # Simulacija mrežnog čekanja (1 sekunda)
        await asyncio.sleep(1)

        # Simulirani podaci o brzinama 100 vozila
        speeds = [random.randint(30, 130) for _ in range(100)]
        average_speed = sum(speeds) / len(speeds)

        print(f"Kamera {camera_id}: prosječna brzina {average_speed:.1f} km/h")
        return average_speed


async def main():
    start = time.perf_counter()

    semaphore = asyncio.Semaphore(5)

    tasks = [process_camera(i, semaphore) for i in range(1, 101)]

    results = await asyncio.gather(*tasks)

    elapsed = time.perf_counter() - start

    print(f"\nObrađeno kamera: {len(results)}")
    print(f"Ukupno vrijeme: {elapsed:.2f} s")


asyncio.run(main())
