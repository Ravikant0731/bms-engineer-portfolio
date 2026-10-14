import asyncio
import BAC0

async def main():
    async with BAC0.start(
        port=47809,
        deviceId=2001,
        localObjName="Discovery-Client"
    ) as bacnet:
        print("Sending directed Who-Is to 172.31.26.179:47808...")
        iams = await bacnet.who_is(address='172.31.26.179:47808')

        print(f"\n{len(iams)} device(s) discovered:\n")
        for iam in iams:
            print(f"  Device Instance : {iam.iAmDeviceIdentifier[1]}")
            print(f"  Max APDU Length : {iam.maxAPDULengthAccepted}")
            print(f"  Segmentation    : {iam.segmentationSupported}")
            print(f"  Vendor ID       : {iam.vendorID}")
            print(f"  Source Address  : {iam.pduSource}")
            print("-" * 40)

if __name__ == "__main__":
    asyncio.run(main())
