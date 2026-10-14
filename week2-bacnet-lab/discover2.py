import asyncio
import BAC0

async def main():
    async with BAC0.start(
        port=47809,
        deviceId=2001,
        localObjName="Discovery-Client"
    ) as bacnet:
        print("Sending directed Who-Is...")
        await bacnet.who_is(address='172.31.26.179:47808')
        await asyncio.sleep(3)

        print("\nAll bacnet attributes containing 'device':")
        attrs = [a for a in dir(bacnet) if 'device' in a.lower()]
        print(attrs)

        for a in attrs:
            try:
                val = getattr(bacnet, a)
                print(f"\n{a} = {val}")
            except Exception as e:
                print(f"\n{a} -> error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
