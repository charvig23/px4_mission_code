import asyncio
from mavsdk import System
from mavsdk.mission import MissionItem, MissionPlan
 
async def run():
    drone = System()
    await drone.connect(system_address="udp://:14540")
 
    print("📡 Connecting to drone...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("✅ Drone connected")
            break
 
    # Define square corners (~10m side)
    origin_lat = 47.397751
    origin_lon = 8.545607
    offset = 0.00009  # ~10 meters in degrees
 
    corners = [
        (origin_lat, origin_lon),
        (origin_lat, origin_lon + offset),
        (origin_lat + offset, origin_lon + offset),
        (origin_lat + offset, origin_lon),
        (origin_lat, origin_lon),  # return to start
    ]
 
    print("📍 Square corners:")
    for i, (lat, lon) in enumerate(corners):
        print(f"   ▪️ Corner {i+1}: lat={lat:.6f}, lon={lon:.6f}")
 
    # Create mission items
    mission_items = []
    for lat, lon in corners:
        mission_items.append(MissionItem(
            latitude_deg=lat,
            longitude_deg=lon,
            relative_altitude_m=10.0,
            speed_m_s=5.0,
            is_fly_through=True,
            gimbal_pitch_deg=0.0,
            gimbal_yaw_deg=0.0,
            camera_action=MissionItem.CameraAction.NONE,
            loiter_time_s=0.0,
            camera_photo_interval_s=0.0,
            acceptance_radius_m=2.0,
            yaw_deg=float('nan'),
            camera_photo_distance_m=0.0,
        ))
 
    await drone.mission.set_return_to_launch_after_mission(False)
    await drone.mission.upload_mission(MissionPlan(mission_items))
    await drone.mission.start_mission()
 
    # Wait until final waypoint is reached
    total_waypoints = len(mission_items)
    async for progress in drone.mission.mission_progress():
        if progress.current == total_waypoints - 1:
            print("✅ Mission complete. Landing now...")
            await drone.action.land()
            break
 
if __name__ == "__main__":
    asyncio.run(run())
