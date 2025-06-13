import asyncio
from mavsdk import System
 
TEMPERATURE_THRESHOLD = 16.0  # Celsius
HOVER_DURATION = 15  # seconds
 
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
        if health.is_global_position_ok and health.is_gyrometer_calibration_ok:
            print("✅ Drone ready for flight")
            break
 
    print("🚁 Arming and taking off...")
    await drone.action.arm()
    await drone.action.takeoff()
    await asyncio.sleep(5)
 
    print("🌡️ Monitoring temperature during hover...")
    try:
        await asyncio.wait_for(monitor_temperature_and_land(drone), timeout=HOVER_DURATION)
    except asyncio.TimeoutError:
        print("⏱️ Hover duration over. Landing...")
        await drone.action.land()
 
async def monitor_temperature_and_land(drone):
    async for imu in drone.telemetry.imu():
        temp = imu.temperature_degc
        print(f"🌡️ Temperature: {temp:.2f} °C")
        if temp > TEMPERATURE_THRESHOLD:
            print(f"🚨 Temperature too high! ({temp:.2f} °C). Landing...")
            await drone.action.land()
            break
        await asyncio.sleep(1)
 
if __name__ == "__main__":
    asyncio.run(run())
