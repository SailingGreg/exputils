#
#

import asyncio
import array
from bleak import discover
from bleak import BleakClient

address = 'd1:6e:f5:06:0d:93'
#address = '40:1C:83:C9:9F:81'
#UUID_NORDIC_TX = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
UUID_NORDIC_TX = '6e400002-b5a3-f393-e0a9-e50e24dcca9e'
#UUID_NORDIC_RX = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"
UUID_NORDIC_RX = '6e400003-b5a3-f393-e0a9-e50e24dcca9e'
command = b"\x03\x10clearInterval()\n\x10setInterval(function() {LED.toggle()}, 500);\n\x10print('Hello World')\n"

def uart_data_recieved(sender, data):
    print("RX> {0}".format(data))

print("Connecting")
async def run(address, loop):
    async with BleakClient(address, loop=loop) as client:
        print("Connected")
        await client.start_notify(UUID_NORDIC_RX, uart_data_recieved)
        print("Writing command")
        c=command
        while len(c)> 0:
            await client.write_gatt_char(UUID_NORDIC_TX, bytearray(c[0:20]), True)
            c = c[20:]
        print ("Waiting for data")
        await asyncio.sleep(1.0, loop=loop) # wait for a response
        print ("Done")

loop = asyncio.get_event_loop()
loop.run_until_complete(run(address, loop))