import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
from ultralytics import YOLO
import requests
import json

bridge = CvBridge()
model = YOLO("yolov8n.pt")  # or yolov8s.pt based on what's available

def query_llm(prompt):
    try:
        payload = {
            "model": "llama3.2",
            "prompt": prompt,
            "stream": True
        }

        response = requests.post("http://localhost:11434/api/generate", json=payload, stream=True)

        print(" LLM Summary:")
        for line in response.iter_lines():
            if line:
                data = json.loads(line.decode('utf-8'))
                print(data.get("response", ""), end='', flush=True)
        print("\n---")
    except Exception as e:
        print(f" Error contacting LLM: {e}")

def image_callback(msg):
    try:
        frame = bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        results = model(frame)[0]  # Run YOLO

        detected = set()
        for box in results.boxes:
            cls_id = int(box.cls[0])
            label = model.names[cls_id]
            detected.add(label)

        object_list = ", ".join(sorted(detected)) or "nothing"
        prompt = f"The drone camera sees the following objects: {object_list}. Describe the surroundings based on this."

        print(f" Detected objects: {object_list}")
        query_llm(prompt)

    except Exception as e:
        print(f" Error in image processing: {e}")

def main():
    rospy.init_node('aruco_llm_object_summary_node')
    rospy.Subscriber('/aruco_cam/camera/link/camera/image_raw', Image, image_callback)
    print(" Listening for camera input and sending summary to LLM...")
    rospy.spin()

if __name__ == '__main__':
    main()
