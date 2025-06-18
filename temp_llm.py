import asyncio
import requests
import json
import os
from mavsdk import System
from datetime import datetime

# Setup log file in current folder
LOG_FILE = os.path.join(os.path.dirname(__file__), "llm_drone_log.txt")

def log(message):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOG_FILE, "a") as f:
        f.write(f"{timestamp} {message}\n")
    print(message)

# Query LLM with temperature
def query_llm_for_action(temp):
    prompt = f"The drone's temperature is {temp:.2f}°C. Should it land or continue hovering? Reply only with 'land' or 'hover'."
    log(f"🔍 Sending to LLM: {prompt}")

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
                    log(f"⚠️ Decode error: {e}")
        
        action = full_output.strip().lower()
        log(f"🧠 LLM Response: {action}")
        return action
    except Exception as e:
        log(f"❌ Error contacting LLM: {e}")
        return "hover"

# Temperature monitoring logic
async def monitor_temperature(drone):
    iteration = 0
    async for imu in drone.telemetry.imu():
        temp = imu.temperature_degc
        log(f"\n🔁 Iteration {iteration + 1} | 🌡️ Temperature: {temp:.2f} °C")

        if temp > 15.0:
            log("🚨 Temperature > 15°C → Landing immediately.")
            await drone.action.land()
            break
        else:
            log("✅ Temperature <= 15°C → Asking LLM...")
            action = query_llm_for_action(temp)

            if "land" in action:
                log("🚨 LLM advised landing → Executing.")
                await drone.action.land()
                break
            else:
                log("🛑 LLM advised to hover.")

        iteration += 1
        if iteration >= 3:
            log("📴 Completed 3 checks. Exiting.")
            break

        await asyncio.sleep(1)

# Main control
async def run():
    drone = System()
    await drone.connect(system_address="udp://:14540")
    log("📡 Connecting to drone...")

    async for state in drone.core.connection_state():
        if state.is_connected:
            log("✅ Drone connected!")
            break

    log("⏳ Waiting for drone readiness...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_gyrometer_calibration_ok:
            log("✅ Drone ready for flight.")
            break

    log("🚁 Arming and taking off...")
    await drone.action.arm()
    await drone.action.takeoff()
    await asyncio.sleep(5)

    log("📈 Starting temperature monitoring with LLM reasoning...")
    await monitor_temperature(drone)

if __name__ == "__main__":
    asyncio.run(run())
