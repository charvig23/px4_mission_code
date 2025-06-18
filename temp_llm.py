import asyncio
import requests
import json
from mavsdk import System

LOW_TEMP_THRESHOLD = 15.0
CONSECUTIVE_LOW_LIMIT = 5

def query_llm_for_action(temp):
    prompt = f"The drone's temperature is {temp:.2f}°C. Should it land or continue hovering? Reply only with 'land' or 'hover'."

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama3", "prompt": prompt, "stream": True},
            stream=True
        )

        full_output = ""
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode('utf-8'))
                    full_output += data.get("response", "")
                except Exception as e:
                    print(f"⚠️ Decode error: {e}")
        
        action = full_output.strip().lower()
        return action
    except Exception as e:
        print(f"❌ Error contacting LLM: {e}")
        return "hover"  # Safe fallback

async def monitor_temperature_and_respond(drone):
    consecutive_low = 0

    async for imu in drone.telemetry.imu():
        temp = imu.temperature_degc
        print(f"🌡️ Temperature: {temp:.2f} °C")

        if temp <= LOW_TEMP_THRESHOLD:
            consecutive_low += 1
            print(f"ℹ️ Low temperature detected ({consecutive_low} in a row)")

            if consecutive_low >= CONSECUTIVE_LOW_LIMIT:
                print("🚨 Temperature low for too long. Landing...")
                await drone.action.land()
                break
        else:
            consecutive_low = 0
            action = query_llm_for_action(temp)
            print(f"🤖 LLM Decision: {action}")

            if "land" in action:
                print("🚨 LLM advised landing. Executing...")
                await drone.action.land()
                break

        await asyncio.sleep(1)

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

