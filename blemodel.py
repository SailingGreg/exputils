import asyncio
from bleak import BleakClient

#address = "24:71:89:cc:09:05"
address = "D1:6E:F5:06:0D:93" # bangle v1
#address = "C0:F6:17:18:BD:BF" # bangle v2
MODEL_NBR_UUID = "00002a24-0000-1000-8000-00805f9b34fb"

async def run(address):
    async with BleakClient(address) as client:
        model_number = await client.read_gatt_char(MODEL_NBR_UUID)
        print("Model Number: {0}".format("".join(map(chr, model_number))))

loop = asyncio.get_event_loop()
loop.run_until_complete(run(address))