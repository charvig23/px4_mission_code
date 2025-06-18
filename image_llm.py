import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import requests
import base64
import json

bridge = CvBridge()

def image_callback(msg):
    try:
        # Convert ROS image to OpenCV format
        frame = bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        cv2.imwrite("/tmp/frame.jpg", frame)  # Save image

        print("📷 Frame captured from Gazebo camera")

        # Convert image to base64
        with open("/tmp/frame.jpg", "rb") as img_file:
            b64_image = base64.b64encode(img_file.read()).decode('utf-8')

        # Send to LLM (LLaVA via Ollama)
        payload = {
            "model": "llava",
            "prompt": "Describe the surroundings shown in this drone camera image.",
            "images": [b64_image]
        }

        response = requests.post("http://localhost:11434/api/generate", json=payload, stream=True)

        print("🤖 LLM Summary:")
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode('utf-8'))
                    print(data.get("response", ""), end='', flush=True)
                except Exception as e:
                    print(f"\n⚠️ Error decoding LLM output: {e}")
        print("\n---")

    except Exception as e:
        print(f"❌ Error processing image: {e}")

def main():
    rospy.init_node('aruco_llm_summary_node')
    rospy.Subscriber('/aruco_cam/camera/link/camera/image_raw', Image, image_callback)
    print("🚀 Listening to camera topic and waiting for frames...")
    rospy.spin()

if __name__ == '__main__':
    main()
