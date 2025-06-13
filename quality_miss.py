import asyncio
from mavsdk import System
 
# Thresholds
MIN_SATELLITES = 6
MIN_FIX_TYPE = 3  # 3D Fix
 
async def run():
    drone = System()
    await drone.connect(system_address="udp://:14540")
    print("📡 Connecting to drone...")
 
    # Wait until connected
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("✅ Drone connected!")
            break
 
    # Wait for global position and sensors to be ready
    print("⏳ Waiting for drone readiness...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_gyrometer_calibration_ok:
            print("✅ Drone is ready")
            break
 
    # Arm and takeoff
    print("🚁 Arming and taking off...")
    await drone.action.arm()
    await drone.action.takeoff()
    await asyncio.sleep(5)
 
    # Monitor GPS
    print("📍 Monitoring GPS quality...")
    await monitor_gps_quality_and_act(drone)
 
async def monitor_gps_quality_and_act(drone):
    async for gps in drone.telemetry.gps_info():
        print(f"📡 Satellites: {gps.num_satellites}, Fix type: {gps.fix_type}")
 
        if gps.num_satellites < MIN_SATELLITES or gps.fix_type < MIN_FIX_TYPE:
            print("⚠️ Poor GPS quality detected! Landing immediately.")
            await drone.action.land()
            break
 
        await asyncio.sleep(1)
 
if __name__ == "__main__":
    asyncio.run(run())
