import asyncio
from mavsdk import System
from mavsdk import mission
from mavsdk.mission import MissionPlan
 
async def run():
    drone = System()
    await drone.connect(system_address="udp://:14540")
 
    print("Waiting for drone connection...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("✅ Drone connected!")
            break
 
    print("Uploading mission...")
    await upload_mission(drone)
 
    print("Monitoring battery during mission...")
    await monitor_battery(drone)
 
async def upload_mission(drone):
    # Define coordinates
    launch_lat = 47.39803986
    launch_lon = 8.54557254
    target_lat = 47.39803622
    target_lon = 8.54501464
    alt = 10  # altitude in meters
 
    mission_items = [
        mission.MissionItem(
            latitude_deg=target_lat,
            longitude_deg=target_lon,
            relative_altitude_m=alt,
            speed_m_s=5.0,
            is_fly_through=True,
            gimbal_pitch_deg=0.0,
            gimbal_yaw_deg=0.0,
            camera_action=mission.MissionItem.CameraAction.NONE,
            loiter_time_s=0.0,
            camera_photo_interval_s=0.0,
            acceptance_radius_m=5.0,
            yaw_deg=float('nan'),
            camera_photo_distance_m=0.0,
        ),
        mission.MissionItem(
            latitude_deg=launch_lat,
            longitude_deg=launch_lon,
            relative_altitude_m=alt,
            speed_m_s=5.0,
            is_fly_through=True,
            gimbal_pitch_deg=0.0,
            gimbal_yaw_deg=0.0,
            camera_action=mission.MissionItem.CameraAction.NONE,
            loiter_time_s=0.0,
            camera_photo_interval_s=0.0,
            acceptance_radius_m=5.0,
            yaw_deg=float('nan'),
            camera_photo_distance_m=0.0,
        )
    ]
 
    await drone.mission.set_return_to_launch_after_mission(True)
    await drone.mission.upload_mission(MissionPlan(mission_items))
    await drone.mission.start_mission()
 
async def monitor_battery(drone):
    async for battery in drone.telemetry.battery():
        print(f"🔋 Battery: {battery.remaining_percent * 100:.1f}%")
        if battery.remaining_percent < 0.3:
            print("⚠️ Battery low! Landing...")
            await drone.action.land()
            break
 
if __name__ == "__main__":
    asyncio.run(run())
