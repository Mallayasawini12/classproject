from flask import Flask, render_template, Response, jsonify, send_file
import cv2
from deepface import DeepFace
from collections import Counter
import threading
import datetime
import json
import csv
import io
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global variables
emotion_counter = Counter()
emotion_history = []  # Store history with timestamps
lock = threading.Lock()
session_start_time = datetime.datetime.now()

camera = cv2.VideoCapture(0)

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break

        try:
            result = DeepFace.analyze(
                frame,
                actions=['emotion'],
                enforce_detection=False,
                silent=True
            )

            emotion = result[0]['dominant_emotion']
            emotion_scores = result[0]['emotion']
            
            # Map 'sad' to 'cry' for better user understanding
            display_emotion = 'cry' if emotion == 'sad' else emotion
            counter_emotion = 'cry' if emotion == 'sad' else emotion

            with lock:
                emotion_counter[counter_emotion] += 1
                # Track history with timestamp (limit to last 100 entries)
                emotion_history.append({
                    'emotion': counter_emotion,
                    'timestamp': datetime.datetime.now().isoformat(),
                    'scores': emotion_scores
                })
                if len(emotion_history) > 100:
                    emotion_history.pop(0)

            # Draw emotion and confidence
            cv2.putText(frame, f'Emotion: {display_emotion}', (30, 40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 255, 0), 2)
            
            # Show top 3 emotions with scores
            y_offset = 80
            sorted_emotions = sorted(emotion_scores.items(), key=lambda x: x[1], reverse=True)[:3]
            for emo, score in sorted_emotions:
                display_emo = 'cry' if emo == 'sad' else emo
                cv2.putText(frame, f'{display_emo}: {score:.1f}%', (30, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX,
                           0.6, (255, 255, 0), 1)
                y_offset += 30

        except Exception as e:
            # Draw error message
            cv2.putText(frame, 'No face detected', (30, 40),
                       cv2.FONT_HERSHEY_SIMPLEX,
                       0.7, (0, 0, 255), 2)
            pass

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/dashboard')
def dashboard():
    with lock:
        total_detections = sum(emotion_counter.values())
        session_duration = datetime.datetime.now() - session_start_time
    
    return render_template("dashboard.html",
                           data=dict(emotion_counter),
                           date=datetime.datetime.now(),
                           total=total_detections,
                           duration=str(session_duration).split('.')[0])

# API Endpoints
@app.route('/api/emotions')
def api_emotions():
    """Get current emotion statistics"""
    with lock:
        data = {
            'emotions': dict(emotion_counter),
            'total_detections': sum(emotion_counter.values()),
            'session_start': session_start_time.isoformat(),
            'session_duration': str(datetime.datetime.now() - session_start_time).split('.')[0],
            'timestamp': datetime.datetime.now().isoformat()
        }
    return jsonify(data)

@app.route('/api/history')
def api_history():
    """Get emotion history"""
    with lock:
        return jsonify({
            'history': emotion_history[-50:],  # Last 50 entries
            'count': len(emotion_history)
        })

@app.route('/api/reset', methods=['POST'])
def api_reset():
    """Reset all emotion statistics"""
    global emotion_counter, emotion_history, session_start_time
    
    try:
        with lock:
            emotion_counter.clear()
            emotion_history.clear()
            session_start_time = datetime.datetime.now()
        
        logger.info("Statistics reset successfully")
        return jsonify({
            'success': True,
            'message': 'Statistics reset successfully',
            'timestamp': datetime.datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error resetting statistics: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/export/json')
def export_json():
    """Export emotion data as JSON"""
    with lock:
        data = {
            'session_info': {
                'start_time': session_start_time.isoformat(),
                'export_time': datetime.datetime.now().isoformat(),
                'duration': str(datetime.datetime.now() - session_start_time).split('.')[0]
            },
            'statistics': dict(emotion_counter),
            'total_detections': sum(emotion_counter.values()),
            'history': emotion_history
        }
    
    # Create JSON file in memory
    json_str = json.dumps(data, indent=2)
    buffer = io.BytesIO(json_str.encode())
    buffer.seek(0)
    
    filename = f'emotion_data_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    
    return send_file(
        buffer,
        mimetype='application/json',
        as_attachment=True,
        download_name=filename
    )

@app.route('/api/export/csv')
def export_csv():
    """Export emotion data as CSV"""
    with lock:
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow(['Timestamp', 'Emotion', 'Count'])
        
        # Write summary data
        writer.writerow([])
        writer.writerow(['Summary Statistics'])
        writer.writerow(['Session Start', session_start_time.isoformat()])
        writer.writerow(['Export Time', datetime.datetime.now().isoformat()])
        writer.writerow(['Total Detections', sum(emotion_counter.values())])
        writer.writerow([])
        
        # Write emotion counts
        writer.writerow(['Emotion Distribution'])
        for emotion, count in emotion_counter.items():
            writer.writerow(['-', emotion.capitalize(), count])
        
        writer.writerow([])
        writer.writerow(['Detailed History'])
        writer.writerow(['Timestamp', 'Emotion'])
        
        # Write history
        for entry in emotion_history:
            writer.writerow([entry['timestamp'], entry['emotion'].capitalize()])
        
        # Convert to bytes
        output.seek(0)
        buffer = io.BytesIO(output.getvalue().encode('utf-8'))
        buffer.seek(0)
    
    filename = f'emotion_data_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    return send_file(
        buffer,
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )

# Additional Pages
@app.route('/about')
def about():
    """About page with information about the technology"""
    return render_template('about.html')

@app.route('/help')
def help_page():
    """Help and documentation page"""
    return render_template('help.html')

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    """Custom 404 error page"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    """Custom 500 error page"""
    logger.error(f"Internal error: {e}")
    return render_template('404.html'), 500

if __name__ == "__main__":
    import os
    
    logger.info("Starting EmotiSense Application...")
    logger.info(f"Session started at: {session_start_time}")
    
    # Get configuration from environment variables
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_PORT', 5000))
    
    try:
        app.run(debug=debug_mode, host=host, port=port)
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
    finally:
        if camera.isOpened():
            camera.release()
        logger.info("Camera released")
