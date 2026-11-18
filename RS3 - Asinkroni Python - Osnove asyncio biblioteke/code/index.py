import time
import asyncio


def main():
    print("Start")

    try:
        loop = asyncio.get_running_loop()
        print("Event loop running:", loop.is_running())
    except RuntimeError:
        print("No event loop is running")

    time.sleep(2)
    print("End")


main()
