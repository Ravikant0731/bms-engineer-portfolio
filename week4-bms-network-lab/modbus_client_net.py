from pymodbus.client import ModbusTcpClient

client = ModbusTcpClient('10.10.20.12', port=502)
client.connect()

print("Reading holding registers (Voltage, Current, Power)...")
result = client.read_holding_registers(address=0, count=3)

if result.isError():
    print("Error reading registers:", result)
else:
    print(f"Raw registers : {result.registers}")
    print(f"Voltage : {result.registers[0] / 10} V")
    print(f"Current : {result.registers[1] / 10} A")
    print(f"Power   : {result.registers[2]} W")

client.close()
