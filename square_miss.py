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
 
    # Define square coordinates
    origin_lat = 47.397751
    origin_lon = 8.545607
    side_offset = 0.00009  # ~10 meters
 
    corners = [
        (origin_lat, origin_lon),
        (origin_lat, origin_lon + side_offset),
        (origin_lat + side_offset, origin_lon + side_offset),
        (origin_lat + side_offset, origin_lon),
        (origin_lat, origin_lon),  # back to start
    ]
 
    print("📍 Waypoints:")
    for i, (lat, lon) in enumerate(corners):
        print(f"  ▪️ Corner {i+1}: lat={lat:.6f}, lon={lon:.6f}")
 
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
            acceptance_radius_m=1.0,
            yaw_deg=float('nan'),
            camera_photo_distance_m=0.0,
        ))
 
    await drone.mission.set_return_to_launch_after_mission(False)
    await drone.mission.upload_mission(MissionPlan(mission_items))
 
    print("🚀 Starting mission...")
    await drone.mission.start_mission()
 
    # Wait for mission to finish
    async for is_finished in drone.mission.mission_finished():
        if is_finished:
            print("✅ Mission done. Landing...")
            await drone.action.land()
            break
 
if __name__ == "__main__":
    asyncio.run(run())
