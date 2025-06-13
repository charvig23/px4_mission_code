import asyncio
from mavsdk import System
 
HDOP_THRESHOLD = 1.5  # Horizontal Dilution of Precision (lower is better)
 
async def run():
    drone = System()
    await drone.connect(system_address="udp://:14540")
 
    print("📡 Connecting to drone...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("✅ Drone connected!")
            break
 
    # Wait for GPS to be ready
    print("📡 Checking GPS status...")
    async for gps in drone.telemetry.gps_info():
        print(f"🛰️ Satellites: {gps.num_satellites}, HDOP: {gps.hdop}")
        if gps.hdop < HDOP_THRESHOLD:
            print("✅ GPS quality is good. Starting mission...")
            break
        else:
            print("❌ GPS accuracy poor. Waiting...")
        await asyncio.sleep(1)
 
    # Arm and take off
    await drone.action.arm()
    await drone.action.takeoff()
    await asyncio.sleep(5)
 
    # Monitor GPS during flight
    await monitor_gps_quality(drone)
 
async def monitor_gps_quality(drone):
    async for gps in drone.telemetry.gps_info():
        print(f"📡 HDOP: {gps.hdop}")
        if gps.hdop > HDOP_THRESHOLD:
            print(f"⚠️ GPS accuracy dropped! Returning to launch...")
            await drone.action.return_to_launch()
            break
        await asyncio.sleep(1)
 
if __name__ == "__main__":
    asyncio.run(run())
