from pymodbus.client import ModbusTcpClient

print("=== TEST 1: Wrong port (5021 instead of 5020) ===")
client = ModbusTcpClient('127.0.0.1', port=5021, timeout=2)
connected = client.connect()
print(f"Connected: {connected}")
try:
    result = client.read_holding_registers(address=0, count=3)
    print(f"Result: {result}")
except Exception as e:
    print(f"Exception: {type(e).__name__}: {e}")
client.close()

print()
print("=== TEST 2: Wrong register address (50, outside 0-9) ===")
client = ModbusTcpClient('127.0.0.1', port=5020, timeout=2)
client.connect()
result = client.read_holding_registers(address=50, count=3)
print(f"isError: {result.isError()}")
print(f"Result: {result}")
client.close()

print()
print("=== FIXED: Correct port and address ===")
client = ModbusTcpClient('127.0.0.1', port=5020, timeout=2)
client.connect()
result = client.read_holding_registers(address=0, count=3)
print(f"Registers: {result.registers}")
client.close()
