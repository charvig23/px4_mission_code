import asyncio
from mavsdk import System
from mavsdk import mission
from mavsdk.mission import MissionItem, MissionPlan
 
# Convert meters to degrees roughly (valid for small distances)
METER_TO_DEG = 1 / 111_000.0  # ~0.000009° ≈ 1 m
 
async def run():
    drone = System()
    await drone.connect(system_address="udp://:14540")
 
    print("📡 Connecting to drone...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("✅ Drone connected!")
            break
 
    print("⏳ Waiting for telemetry health...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("✅ Global position ready")
            break
 
    # Get current position as launch point
    async for pos in drone.telemetry.position():
        launch_lat = pos.latitude_deg
        launch_lon = pos.longitude_deg
        break
 
    square_size_m = 1
    offset_deg = square_size_m * METER_TO_DEG
 
    # Define square corners clockwise
    corners = [
        (launch_lat, launch_lon),  # Start
        (launch_lat, launch_lon + offset_deg),  # Right
        (launch_lat + offset_deg, launch_lon + offset_deg),  # Down-Right
        (launch_lat + offset_deg, launch_lon),  # Down
        (launch_lat, launch_lon),  # Back to start
    ]
 
    # Print the coordinates
    print("📍 Mission waypoints:")
    for i, (lat, lon) in enumerate(corners):
        print(f"  🔹 Corner {i+1}: lat={lat:.6f}, lon={lon:.6f}")
 
    mission_items = []
    for lat, lon in corners:
        mission_items.append(MissionItem(
            latitude_deg=lat,
            longitude_deg=lon,
            relative_altitude_m=10.0,
            speed_m_s=3.0,
            is_fly_through=True,
            gimbal_pitch_deg=0.0,
            gimbal_yaw_deg=0.0,
            camera_action=MissionItem.CameraAction.NONE,
            loiter_time_s=0.0,
            camera_photo_interval_s=0.0,
            acceptance_radius_m=2.0,
            yaw_deg=float('nan'),
            camera_photo_distance_m=0.0
        ))
 
    # Upload and start mission
    await drone.mission.set_return_to_launch_after_mission(True)
    await drone.mission.upload_mission(MissionPlan(mission_items))
    print("📤 Mission uploaded. Starting...")
    await drone.mission.start_mission()
 
    # Monitor progress
    async for mission_progress in drone.mission.mission_progress():
        print(f"🚀 Waypoint: {mission_progress.current + 1}/{mission_progress.total}")
        if mission_progress.current == mission_progress.total - 1:
            print("✅ Mission complete.")
            break
 
if __name__ == "__main__":
    asyncio.run(run())
