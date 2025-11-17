import time, asyncio

async def fetch_data(param):
    print(f"Nešto radim s {param}")
    await asyncio.sleep(int(param))
    print(f"Dovršio sam s {param}")
    return f"Rezultat izvođenja za {param}"

async def main():
    task_1 = asyncio.create_task(fetch_data(1)) # schedule
    task_2 = asyncio.create_task(fetch_data(2)) # schedule
    
    #rezultat_2 = await task_2 # wait for result of task_2
    #print(f"Fetch 2 uspješno završen!")

    rezultat_1 = await task_1 # run task_1, task_2
    print(f"Fetch 1 uspješno završen!")

    await asyncio.sleep(1)

    return [rezultat_1]

if __name__ == '__main__':
    t1 = time.perf_counter()
    rezultati = asyncio.run(main()) # start event loop, schedule main, run main
    t2 = time.perf_counter()
    print(f"Vrijeme izvođenja {t2 - t1:.2f}")
    print(f"Rezultati: {rezultati}")