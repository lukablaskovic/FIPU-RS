import asyncio
import random
from datetime import datetime

async def get_camera_data(camera_id: int) -> dict:
    cekanje = random.uniform(0.1, 5)
    await asyncio.sleep(cekanje + 0.5)
    data = {
        "camera_id": camera_id,
        "timestamp": datetime.now().isoformat(),
        "vehicle_count": random.randint(5, 20)
    }
    return data


async def test():
    print(f"Čekam podatke kamere 1")
    kamera_1_rez = await get_camera_data(1)

    print(f"Čekam podatke kamere 2")
    kamera_2_rez =await get_camera_data(2)

    print(kamera_1_rez, kamera_2_rez, sep="\n")

# asyncio.run(test())

async def main():
    # centralni poslužitelj
    MAX_DURATION = 30 # sec
    CYCLE_DURATION = 5
    CYCLE_COUNT = MAX_DURATION // CYCLE_DURATION

    total_rezultati = []
    for cycle_n in range(1, CYCLE_COUNT + 1):
        print(f"Započinjem cycle {cycle_n}...")
        korutine = [get_camera_data(i) for i in range(1, 6)]

        taskovi = [asyncio.wait_for(asyncio.create_task(korutina), timeout=3) for korutina in korutine]

        rezultati = await asyncio.gather(*taskovi, return_exceptions=True)
        
        print(rezultati)

        #for rezultat in rezultati:
        #    print(rezultat)

        # za 4.3
        rezultati = [rezultat for rezultat in rezultati if not isinstance(rezultat, Exception or TimeoutError)]
        total_rezultati.append(rezultati)

        kamera_timestamp = [(element["camera_id"], element["timestamp"]) for element in rezultati]
        print(kamera_timestamp)

        najstariji_ts = min(kamera_timestamp, key= lambda ts_tuple : datetime.fromisoformat(ts_tuple[1]))
        najnoviji_ts = max(kamera_timestamp, key= lambda ts_tuple : datetime.fromisoformat(ts_tuple[1]))
        print("najstariji_ts", najstariji_ts)
        print("najnoviji_ts", najnoviji_ts)

        ukupan_broj_vozila = sum(element["vehicle_count"] for element in rezultati)

        print(f"Ukupan broj vozila u ciklusu: {ukupan_broj_vozila}")
    
    print("Total rezultati nakon svih ciklusa:", total_rezultati, sep="\n")

    camera_data = {i : [] for i in range(1,6)}

    for i, cycle in enumerate(total_rezultati):
        print(f"cycle {i+1}:\n {cycle}")

        for result in cycle:
            camera_data[result["camera_id"]].append(result["vehicle_count"])
        
        print(camera_data)

    avg_po_kameri = {kamera : round(sum(vrijednosti)/len(vrijednosti), 2) for kamera, vrijednosti in camera_data.items()}

    print("avg_po_kameri", avg_po_kameri, sep="\n")

    # očekivanja struktura

    """
    {
    "camera_1" : avg,
    "camera_2" : avg,
    "camera_3" : avg,
    "camera_4" : avg,
    "camera_5" : avg,
    }
    """

asyncio.run(main())