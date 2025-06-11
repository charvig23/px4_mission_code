import asyncio
from mavsdk import System
 
async def run():
    drone = System()
    await drone.connect(system_address="udp://:14540")
 
    print("Waiting for drone connection...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Hello World: Drone connected!")
            break
 
if __name__ == "__main__":
    asyncio.run(run())