import asyncio
from pymodbus.server import StartAsyncTcpServer
from pymodbus.datastore import ModbusServerContext, ModbusSequentialDataBlock

try:
    from pymodbus.datastore import ModbusDeviceContext as DeviceContext
except ImportError:
    from pymodbus.datastore import ModbusSlaveContext as DeviceContext

# Simulated energy meter, holding registers (block 1 se start hota hai, client address 0 se padhega):
# Register 0: Voltage (2305 = 230.5V, scaled x10)
# Register 1: Current (125 = 12.5A, scaled x10)
# Register 2: Power (5000 = 5000W)
block = ModbusSequentialDataBlock(1, [2305, 125, 5000, 0, 0, 0, 0, 0, 0, 0])
store = DeviceContext(hr=block)

try:
    context = ModbusServerContext(devices=store, single=True)
except TypeError:
    context = ModbusServerContext(slaves=store, single=True)

async def main():
    print("Starting Modbus TCP server (simulated energy meter) on port 502...")
    print("Press Ctrl+C to stop")
    await StartAsyncTcpServer(context=context, address=("0.0.0.0", 502))

if __name__ == "__main__":
    asyncio.run(main())
