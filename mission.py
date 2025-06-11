import asyncio
from mavsdk import System
from mavsdk import mission
 
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
    mission_items = [
        mission.MissionItem(47.39803986, 8.54557254,
                            10, 10, True,
                            mission.MissionItem.CameraAction.NONE, 0, 0, 0, 0,
                            float('nan'), float('nan')),
        mission.MissionItem(47.39803622, 8.54501464,
                            10, 10, True,
                            mission.MissionItem.CameraAction.NONE, 0, 0, 0, 0,
                            float('nan'), float('nan'))
    ]
 
    await drone.mission.set_return_to_launch_after_mission(True)
    await drone.mission.upload_mission(mission_items)
    print("🚀 Mission uploaded. Starting mission...")
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
