import asyncio
from mavsdk import System
 
TEMPERATURE_THRESHOLD = 60.0  # degrees Celsius
 
async def run():
    drone = System()
    await drone.connect(system_address="udp://:14540")
 
    print("📡 Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("✅ Drone connected!")
            break
 
    # Wait for telemetry to be ready
    print("⏳ Waiting for telemetry health...")
    async for health in drone.telemetry.health():
        if health.is_gyrometer_calibration_ok:  # Just a signal it's ready
            print("✅ Telemetry ready")
            break
 
    print("🚁 Monitoring temperature and position...")
 
    # Start monitoring both position and temperature concurrently
    await asyncio.gather(
        monitor_temperature_and_land(drone),
        log_position(drone)
    )
 
 
async def monitor_temperature_and_land(drone):
    async for imu in drone.telemetry.imu_reading_ned():
        temp = imu.temperature_degc
        print(f"🌡️ Temperature: {temp:.2f} °C")
 
        if temp > TEMPERATURE_THRESHOLD:
            print(f"🚨 Temperature too high! ({temp:.2f} °C) Initiating landing...")
            await drone.action.land()
            break
 
        await asyncio.sleep(1)
 
 
async def log_position(drone):
    async for pos in drone.telemetry.position():
        print(f"📍 Drone at lat: {pos.latitude_deg:.6f}, lon: {pos.longitude_deg:.6f}, alt: {pos.relative_altitude_m:.2f} m")
        await asyncio.sleep(1)
 
if __name__ == "__main__":
    asyncio.run(run())