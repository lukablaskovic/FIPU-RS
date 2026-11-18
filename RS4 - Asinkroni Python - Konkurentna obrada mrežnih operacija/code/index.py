import asyncio


async def fetch_camera_data(camera_id):
    print(f"Fetching data from camera {camera_id}...")
    # Simuliramo mrežnu operaciju s različitim vremenima trajanja
    await asyncio.sleep(
        camera_id * 2
    )  # Zahtjev kameri s oznakom 1 traje 2 sekunde, a zahtjev kameri s oznakom 2 traje 4 sekunde itd.
    if camera_id == 3:
        raise Exception(
            "Camera 3 is unreachable!"
        )  # Simuliramo grešku za kameru 3 (kamera koja se nalazi na nepovoljnoj lokaciji)
    print(f"Data from camera {camera_id} fetched.")
    return f"Data from camera {camera_id}"


async def main():
    camera_ids = [1, 2, 3, 4, 5]
    tasks = [fetch_camera_data(camera_id) for camera_id in camera_ids]

    # Primjer asyncio.gather bez timeouta

    try:
        results = await asyncio.gather(*tasks)
        print("All camera data fetched:", results)
    except Exception as e:
        print("An error occurred while fetching camera data:", e)


asyncio.run(main())
