import asyncio
from mavsdk import System
import time
 
MIN_SATELLITES = 8
MIN_FIX_TYPE = 3
GOOD_GPS_DURATION = 10  # seconds to stay in air before landing
 
async def run():
    drone = System()
    await drone.connect(system_address="udp://:14540")
    print("📡 Connecting to drone...")
 
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("✅ Drone connected!")
            break
 
    print("⏳ Waiting for drone to be ready...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok:
            print("✅ Drone ready")
            break
 
    await drone.action.arm()
    await drone.action.takeoff()
    await asyncio.sleep(5)
 
    print("📍 Monitoring GPS quality...")
 
    start_time = time.time()
    async for gps in drone.telemetry.gps_info():
        print(f"📶 Satellites: {gps.num_satellites}, Fix Type: {gps.fix_type}")
 
        if gps.num_satellites < MIN_SATELLITES or gps.fix_type.value < MIN_FIX_TYPE:
            print("⚠️ Poor GPS quality detected! Landing...")
            await drone.action.land()
            return
 
        if time.time() - start_time > GOOD_GPS_DURATION:
            print("✅ Good GPS sustained. Landing after stable flight.")
            await drone.action.land()
            return
 
        await asyncio.sleep(1)
 
if __name__ == "__main__":
    asyncio.run(run())
