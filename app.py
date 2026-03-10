from flask import Flask, render_template, Response, jsonify, send_file, request
import cv2
from deepface import DeepFace
from collections import Counter, deque
import threading
import datetime
import json
import csv
import io
import logging
from pathlib import Path
import base64
import numpy as np
import random

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
session_notes = []  # Store user notes
saved_snapshots = []  # Store captured snapshots
emotion_intensity_history = deque(maxlen=100)  # Track emotion intensity
current_frame = None  # Store current frame for snapshot
sessions_archive = []  # Store past sessions for comparison

camera = cv2.VideoCapture(0)

def generate_frames():
    global current_frame
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
            
            # Calculate emotion intensity (dominant emotion score)
            emotion_intensity = max(emotion_scores.values())

            with lock:
                current_frame = frame.copy()  # Store current frame for snapshots
                emotion_counter[counter_emotion] += 1
                
                # Track history with timestamp (limit to last 100 entries)
                emotion_history.append({
                    'emotion': counter_emotion,
                    'timestamp': datetime.datetime.now().isoformat(),
                    'scores': emotion_scores
                })
                if len(emotion_history) > 100:
                    emotion_history.pop(0)
                
                # Track emotion intensity
                emotion_intensity_history.append({
                    'timestamp': datetime.datetime.now().isoformat(),
                    'emotion': counter_emotion,
                    'intensity': emotion_intensity
                })

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

# NEW FEATURES

@app.route('/api/recommendations')
def api_recommendations():
    """Get activity recommendations based on current emotion"""
    with lock:
        if not emotion_counter:
            return jsonify({'message': 'No emotions detected yet'})
        
        dominant_emotion = emotion_counter.most_common(1)[0][0]
    
    # Emotion-based recommendations
    recommendations = {
        'happy': {
            'activities': ['Share your joy with friends', 'Try something new', 'Help someone in need', 'Celebrate your success'],
            'music': ['Upbeat pop', 'Dance music', 'Feel-good classics'],
            'color': '#FFD700',
            'message': 'You\'re feeling great! Keep spreading positivity!'
        },
        'cry': {
            'activities': ['Talk to a friend', 'Watch a comfort movie', 'Practice self-care', 'Write in a journal'],
            'music': ['Calm acoustic', 'Meditation music', 'Soft piano'],
            'color': '#4682B4',
            'message': 'It\'s okay to feel sad. Take care of yourself.'
        },
        'angry': {
            'activities': ['Go for a walk', 'Try deep breathing', 'Exercise', 'Listen to calming music'],
            'music': ['Calm instrumentals', 'Nature sounds', 'Meditation music'],
            'color': '#FF4500',
            'message': 'Take a moment to breathe and relax.'
        },
        'surprise': {
            'activities': ['Embrace the moment', 'Share your excitement', 'Document the experience'],
            'music': ['Exciting soundtracks', 'Energetic beats'],
            'color': '#FF69B4',
            'message': 'Life is full of surprises! Enjoy this moment!'
        },
        'fear': {
            'activities': ['Practice relaxation', 'Talk to someone', 'Focus on breathing', 'Ground yourself'],
            'music': ['Calming nature sounds', 'Slow tempo music', 'Guided meditation'],
            'color': '#800080',
            'message': 'You\'re safe. Take slow, deep breaths.'
        },
        'disgust': {
            'activities': ['Change your environment', 'Practice mindfulness', 'Focus on positive things'],
            'music': ['Uplifting music', 'Happy tunes'],
            'color': '#228B22',
            'message': 'Shift your focus to something pleasant.'
        },
        'neutral': {
            'activities': ['Try something new', 'Connect with friends', 'Set a new goal', 'Learn something'],
            'music': ['Your favorite genre', 'Discovery playlists'],
            'color': '#808080',
            'message': 'A calm state is perfect for new beginnings!'
        }
    }
    
    recommendation = recommendations.get(dominant_emotion, recommendations['neutral'])
    recommendation['emotion'] = dominant_emotion
    
    return jsonify(recommendation)

@app.route('/api/snapshot', methods=['POST'])
def api_snapshot():
    """Capture current frame as snapshot"""
    global current_frame, saved_snapshots
    
    with lock:
        if current_frame is None:
            return jsonify({'success': False, 'message': 'No frame available'}), 400
        
        # Encode frame to base64
        _, buffer = cv2.imencode('.jpg', current_frame)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        # Get current emotion if available
        current_emotion = emotion_counter.most_common(1)[0][0] if emotion_counter else 'unknown'
        
        snapshot_data = {
            'id': len(saved_snapshots) + 1,
            'timestamp': datetime.datetime.now().isoformat(),
            'emotion': current_emotion,
            'image': f'data:image/jpeg;base64,{img_base64}'
        }
        
        saved_snapshots.append(snapshot_data)
        
        # Keep only last 20 snapshots
        if len(saved_snapshots) > 20:
            saved_snapshots.pop(0)
    
    return jsonify({
        'success': True,
        'message': 'Snapshot captured',
        'snapshot': snapshot_data
    })

@app.route('/api/snapshots')
def api_get_snapshots():
    """Get all saved snapshots"""
    with lock:
        return jsonify({
            'snapshots': saved_snapshots,
            'count': len(saved_snapshots)
        })

@app.route('/api/notes', methods=['GET', 'POST', 'DELETE'])
def api_notes():
    """Manage session notes"""
    global session_notes
    
    if request.method == 'POST':
        data = request.get_json()
        note_text = data.get('note', '')
        
        if not note_text:
            return jsonify({'success': False, 'message': 'Note cannot be empty'}), 400
        
        with lock:
            note = {
                'id': len(session_notes) + 1,
                'text': note_text,
                'timestamp': datetime.datetime.now().isoformat(),
                'emotion': emotion_counter.most_common(1)[0][0] if emotion_counter else 'neutral'
            }
            session_notes.append(note)
        
        return jsonify({'success': True, 'note': note})
    
    elif request.method == 'DELETE':
        note_id = request.args.get('id', type=int)
        with lock:
            session_notes = [n for n in session_notes if n['id'] != note_id]
        return jsonify({'success': True, 'message': 'Note deleted'})
    
    else:  # GET
        with lock:
            return jsonify({
                'notes': session_notes,
                'count': len(session_notes)
            })

@app.route('/api/intensity')
def api_intensity():
    """Get emotion intensity data"""
    with lock:
        intensity_data = list(emotion_intensity_history)
        
        # Calculate average intensity per emotion
        emotion_avg_intensity = {}
        for entry in intensity_data:
            emotion = entry['emotion']
            intensity = entry['intensity']
            if emotion not in emotion_avg_intensity:
                emotion_avg_intensity[emotion] = []
            emotion_avg_intensity[emotion].append(intensity)
        
        # Calculate averages
        for emotion in emotion_avg_intensity:
            intensities = emotion_avg_intensity[emotion]
            emotion_avg_intensity[emotion] = sum(intensities) / len(intensities)
        
        return jsonify({
            'intensity_history': intensity_data[-50:],  # Last 50 entries
            'average_intensity': emotion_avg_intensity,
            'current_intensity': intensity_data[-1]['intensity'] if intensity_data else 0
        })

@app.route('/api/session/save', methods=['POST'])
def api_save_session():
    """Save current session for comparison"""
    global sessions_archive
    
    with lock:
        session_data = {
            'id': len(sessions_archive) + 1,
            'timestamp': datetime.datetime.now().isoformat(),
            'start_time': session_start_time.isoformat(),
            'duration': str(datetime.datetime.now() - session_start_time).split('.')[0],
            'emotions': dict(emotion_counter),
            'total_detections': sum(emotion_counter.values()),
            'dominant_emotion': emotion_counter.most_common(1)[0][0] if emotion_counter else 'none',
            'notes': session_notes.copy()
        }
        
        sessions_archive.append(session_data)
        
        # Keep only last 10 sessions
        if len(sessions_archive) > 10:
            sessions_archive.pop(0)
    
    return jsonify({
        'success': True,
        'message': 'Session saved successfully',
        'session': session_data
    })

@app.route('/api/sessions')
def api_get_sessions():
    """Get all saved sessions"""
    with lock:
        return jsonify({
            'sessions': sessions_archive,
            'count': len(sessions_archive)
        })

@app.route('/api/session/compare')
def api_compare_sessions():
    """Compare two sessions"""
    session1_id = request.args.get('id1', type=int)
    session2_id = request.args.get('id2', type=int)
    
    with lock:
        session1 = next((s for s in sessions_archive if s['id'] == session1_id), None)
        session2 = next((s for s in sessions_archive if s['id'] == session2_id), None)
        
        if not session1 or not session2:
            return jsonify({'success': False, 'message': 'Session not found'}), 404
        
        comparison = {
            'session1': session1,
            'session2': session2,
            'differences': {
                'duration_diff': str(abs(
                    datetime.datetime.fromisoformat(session1['duration']) - 
                    datetime.datetime.fromisoformat(session2['duration'])
                )) if 'T' not in session1['duration'] else 'N/A',
                'detection_diff': session1['total_detections'] - session2['total_detections'],
                'emotion_changes': {}
            }
        }
        
        # Compare emotions
        all_emotions = set(list(session1['emotions'].keys()) + list(session2['emotions'].keys()))
        for emotion in all_emotions:
            count1 = session1['emotions'].get(emotion, 0)
            count2 = session2['emotions'].get(emotion, 0)
            comparison['differences']['emotion_changes'][emotion] = count1 - count2
    
    return jsonify(comparison)

@app.route('/api/stats/advanced')
def api_advanced_stats():
    """Get advanced statistics"""
    with lock:
        if not emotion_counter:
            return jsonify({'message': 'No data available'})
        
        total = sum(emotion_counter.values())
        emotions = dict(emotion_counter)
        
        # Calculate percentages
        percentages = {k: (v/total)*100 for k, v in emotions.items()}
        
        # Calculate emotion diversity (how varied the emotions are)
        diversity_score = len(emotions) / 7 * 100  # 7 total emotions
        
        # Get emotion trends (increasing/decreasing)
        trends = {}
        if len(emotion_history) >= 10:
            recent = emotion_history[-10:]
            for emotion in emotions.keys():
                recent_count = sum(1 for e in recent if e['emotion'] == emotion)
                trends[emotion] = 'increasing' if recent_count > emotions[emotion]/total*10 else 'stable'
        
        # Calculate session quality score
        positive_emotions = emotions.get('happy', 0) + emotions.get('surprise', 0)
        negative_emotions = emotions.get('cry', 0) + emotions.get('angry', 0) + emotions.get('fear', 0)
        quality_score = (positive_emotions / total * 100) if total > 0 else 50
        
        return jsonify({
            'percentages': percentages,
            'diversity_score': diversity_score,
            'trends': trends,
            'quality_score': quality_score,
            'dominant_emotion': emotion_counter.most_common(1)[0][0],
            'rare_emotions': emotion_counter.most_common()[:-4:-1],  # Least common
            'emotion_balance': {
                'positive': positive_emotions,
                'negative': negative_emotions,
                'neutral': emotions.get('neutral', 0)
            }
        })

# Additional Pages
@app.route('/about')
def about():
    """About page with information about the technology"""
    return render_template('about.html')

@app.route('/help')
def help_page():
    """Help and documentation page"""
    return render_template('help.html')

@app.route('/features')
def features_page():
    """Features showcase page"""
    return render_template('features.html')

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
