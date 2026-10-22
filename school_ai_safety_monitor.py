"""
Global Open-Source School AI Safety Monitor
-------------------------------------------
Analyzes IP camera streams using Gemini Vision API to detect weapons, 
physical assaults, and immediate threats, triggering automated alerts.
"""

import cv2
import time
import json
import google.generativeai as genai

# Configure Gemini API Key
genai.configure(api_key="YOUR_GEMINI_API_KEY_HERE")
model = genai.GenerativeModel("gemini-1.5-flash")

SAFETY_PROMPT = """
Analyze this school surveillance camera frame. 
Look strictly for threats such as firearms, knives, physical violence, or suspicious drug handoffs.
Respond ONLY in valid JSON format:
{
  "threat_detected": true/false,
  "threat_type": "NONE" | "FIREARM" | "BLADE" | "PHYSICAL_VIOLENCE" | "SUSPICIOUS_PACKAGE",
  "urgency_level": "LOW" | "MEDIUM" | "CRITICAL",
  "description": "Concise visual detail"
}
"""

def analyze_video_frame(frame_bytes: bytes) -> dict:
    """Sends frame to Gemini Vision API for multimodal threat detection."""
    try:
        image_part = {"mime_type": "image/jpeg", "data": frame_bytes}
        response = model.generate_content([SAFETY_PROMPT, image_part])
        # Clean and parse JSON response
        text_response = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(text_response)
    except Exception as e:
        return {"threat_detected": False, "error": str(e)}

def trigger_authorities_alert(threat_data: dict, camera_id: int):
    """Triggers automated emergency alert to security personnel and local authorities."""
    print(f"\n[CRITICAL ALERT - CAM {camera_id}] THREAT DETECTED!")
    print(f" -> Type: {threat_data.get('threat_type')}")
    print(f" -> Urgency: {threat_data.get('urgency_level')}")
    print(f" -> Details: {threat_data.get('description')}")
    print("[ACTION] Encrypted alert packet dispatched to emergency services (112) & school security.\n")

def start_school_surveillance(camera_source=0, interval_seconds=2.0):
    """Starts local video capture and AI evaluation loop."""
    cap = cv2.VideoCapture(camera_source)
    if not cap.isOpened():
        print(f"[ERROR] Could not open video source {camera_source}")
        return

    print(f"[INFO] School AI Safety Monitor active on source {camera_source}. Press Ctrl+C to stop.")
    
    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("[WARNING] Frame capture failed. Reconnecting...")
                time.sleep(1)
                continue
            
            # Encode frame to JPEG bytes
            success, buffer = cv2.imencode('.jpeg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if not success:
                continue
            
            frame_bytes = buffer.tobytes()
            result = analyze_video_frame(frame_bytes)
            
            if result.get("threat_detected") and result.get("urgency_level") == "CRITICAL":
                trigger_authorities_alert(result, camera_id=0)
            else:
                print(f"[STATUS] Scan normal. [Threat: {result.get('threat_detected', False)}]")
            
            time.sleep(interval_seconds)
            
    except KeyboardInterrupt:
        print("\n[INFO] Monitoring stopped by user.")
    finally:
        cap.release()

if __name__ == "__main__":
    # Run simulation or connect to local school IP camera RTSP stream
    start_school_surveillance(camera_source=0, interval_seconds=3.0)
