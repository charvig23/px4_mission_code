import asyncio

import requests

from mavsdk import System

def query_llm_for_action(temp):

    prompt = f"The drone's temperature is {temp:.2f}°C. Should it land or continue hovering? Reply with only 'land' or 'hover'."

    try:

        response = requests.post(

            "http://localhost:11434/api/generate",

            json={"model": "llama3", "prompt": prompt, "stream": False}

        )

        result = response.json()

        action = result["response"].strip().lower()

        return action

    except Exception as e:

        print(f"❌ Error contacting LLM: {e}")

        return "hover"  # default safe action
 
# Monitor temperature and take action based on LLM reasoning

async def monitor_temperature_and_respond(drone):

    async for imu in drone.telemetry.imu():

        temp = imu.temperature_degc

        print(f"🌡️ Temperature: {temp:.2f} °C")

        action = query_llm_for_action(temp)

        print(f"🤖 LLM Decision: {action}")

        if "land" in action:

            print("🚨 LLM advised landing. Executing...")

            await drone.action.land()

            break

        await asyncio.sleep(1)
 
# Main drone logic

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
 
    print("🌡️ Monitoring temperature with reasoning...")

    await monitor_temperature_and_respond(drone)
 
if __name__ == "__main__":

    asyncio.run(run())
