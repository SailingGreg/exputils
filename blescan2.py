import asyncio
from bleak import BleakScanner

def detection_callback(device, advertisement_data):
    print(device.address, "RSSI:", device.rssi, advertisement_data)

async def run():
    scanner = BleakScanner()
    scanner.register_detection_callback(detection_callback)
    await scanner.start()
    await asyncio.sleep(5.0)
    await scanner.stop()
    
    cnt = 1
    for d in scanner.discovered_devices:
        print(cnt, d)
        cnt = cnt + 1

loop = asyncio.get_event_loop()
loop.run_until_complete(run())