import asyncio
import BAC0

async def main():
    async with BAC0.start(deviceId=1001, localObjName="AHU-Controller-01") as bacnet:
        print("Virtual AHU Controller running as Device 1001")
        print("Press Ctrl+C to stop")
        try:
            while True:
                await asyncio.sleep(5)
        except asyncio.CancelledError:
            print("Device stopped")

if __name__ == "__main__":
    asyncio.run(main())
