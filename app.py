import re
import warnings
from datetime import datetime
import os
from dotenv import load_dotenv
import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import isodate
import random
from flask_mail import Mail, Message
import asyncio
import httpx # === NEW IMPORT ===
import json # === NEW IMPORT ===

# --- Suppress future warnings ---
warnings.filterwarnings("ignore", category=FutureWarning)

# === FLASK APP INITIALIZATION ===
load_dotenv()
app = Flask(__name__)
CORS(app)

# === CONFIGURATION ===
API_KEY = os.getenv("YOUTUBE_API_KEY")
MODEL_PATH = "catboost_dopamine_model.cbm"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY") # === NEW CHATBOT CONFIG ===

if not API_KEY or not OPENROUTER_API_KEY:
    print("❌ CRITICAL ERROR: Ensure 'YOUTUBE_API_KEY' and 'OPENROUTER_API_KEY' are in your .env file.")

# === OTP & MAIL CONFIG ===
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() in ['true', '1', 't']
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
mail = Mail(app)

otp_storage = {}

# --- Load the model once when the app starts ---
try:
    cat_model = CatBoostClassifier()
    model_path = os.path.join(os.path.dirname(__file__), MODEL_PATH)
    cat_model.load_model(model_path)
    print(f"✅ CatBoost model loaded successfully from {model_path}.")
except Exception as e:
    print(f"❌ CRITICAL ERROR: Could not load model from '{model_path}'. Error: {e}")
    cat_model = None

# === DATA MAPPINGS ===
dopamine_factor_map = { "no dominant factor": "No Dominant Factor", "repetitive music/audio": "Repetitive Music/Audio", "catchy/melodic music": "Catchy/Melodic Music", "element of surprise": "Element of Surprise", "on-screen positive feedback": "On-screen Positive Feedback", "game-like progression": "Game-like Progression", "familiar characters": "Familiar Characters", "distinctive sound effects": "Distinctive Sound Effects", "engaging narrative": "Engaging Narrative", "visual effects": "Visual Effects", "unique animation style": "Unique Animation Style", "creative elements": "Creative Elements" }
dominant_color_map = { "no dominant color": "No Dominant Color", "multi colors": "Multi Colors", "blue": "Blue", "pink": "Pink", "white": "White", "violet": "Violet", "peach": "Peach", "green": "Green", "red": "Red", "yellow": "Yellow", "orange": "Orange", "brown": "Brown", "black": "Black", "grey": "Grey", "purple": "Purple" }
video_category_map = { "missing": "Missing", "advertisement": "Advertisement", "country vlog": "Country Vlog", "documentary": "Documentary", "education": "Education", "entertainment": "Entertainment", "food vlog": "Food Vlog", "gaming": "Gaming", "informative": "Informative", "inspirational": "Inspirational", "motivational": "Motivational", "music": "Music", "nature": "Nature", "nursery rhymes": "Nursery Rhymes", "short story": "Short Story", "shots": "Shots", "tourism": "Tourism", "travel vlog": "Travel Vlog", "vlog": "Vlog" }

# === HELPER FUNCTIONS ===
def parse_iso8601_duration(duration_str):
    try: return int(isodate.parse_duration(duration_str).total_seconds())
    except: return 0

def get_video_id_from_url(url):
    match = ( re.search(r"(?<=v=)[\w-]+", url) or re.search(r"(?<=be/)[\w-]+", url) or re.search(r"(?<=embed/)[\w-]+", url) )
    return match.group(0) if match else None

# === NEW ASYNC CHATBOT LOGIC ===
async def stream_chat_from_openrouter(user_message: str):
    """ This async generator function streams responses from the AI service. """
    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    system_message = { "role": "system", "content": "Don't help the user with any coding related tasks, Answer to only dopamine or website related queires" }
    payload = {
        "model": "deepseek/deepseek-chat",
        "messages": [ system_message, {"role": "user", "content": user_message} ],
        "temperature": 0.7,
        "stream": True
    }

    try:
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream("POST", "https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload) as response:
                if response.status_code != 200:
                    error_text = await response.aread()
                    yield f"data: {json.dumps({'error': error_text.decode()})}\n\n"
                    return

                async for line in response.aiter_lines():
                    if line and line.startswith("data: "):
                        json_str = line[6:]
                        if json_str == "[DONE]":
                            break
                        try:
                            data = json.loads(json_str)
                            content = data.get("choices", [{}])[0].get("delta", {}).get("content")
                            if content:
                                # Yield data in SSE format
                                yield f"data: {json.dumps({'content': content})}\n\n"
                        except json.JSONDecodeError:
                            continue
    except Exception as e:
        print(f"❌ Error in stream_chat_from_openrouter: {e}")
        yield f"data: {json.dumps({'error': 'An error occurred while connecting to the AI service.'})}\n\n"


# === NEW CHATBOT API ENDPOINT ===
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message')
    if not user_message:
        return jsonify({'error': 'Message is required'}), 400

    # This function will stream the response from the async generator
    def generate():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        async_generator = stream_chat_from_openrouter(user_message)
        try:
            while True:
                # Get the next chunk from the async generator
                chunk = loop.run_until_complete(anext(async_generator, None))
                if chunk is None:
                    break
                yield chunk
        finally:
            loop.close()

    # Return a streaming response
    return Response(stream_with_context(generate()), mimetype='text/event-stream')


# === OTP & PREDICTION ENDPOINTS ===
# (Your other endpoints remain unchanged)
@app.route('/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json(); email = data.get('email')
    if not email: return jsonify({'error': 'Email is required'}), 400
    otp = str(random.randint(100000, 999999)); otp_storage[email] = otp
    print(f"Generated OTP {otp} for {email}")
    try:
        msg = Message("Your DopamineExp Login Code", sender=app.config['MAIL_USERNAME'], recipients=[email])
        msg.body = f"Your one-time login code is: {otp}"; mail.send(msg)
        return jsonify({'message': 'OTP sent successfully!'}), 200
    except Exception as e:
        print(f"❌ Failed to send email: {e}"); return jsonify({'error': 'Failed to send OTP email.'}), 500

@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json(); email = data.get('email'); user_otp = data.get('otp')
    if not email or not user_otp: return jsonify({'error': 'Email and OTP are required'}), 400
    stored_otp = otp_storage.get(email)
    if stored_otp and stored_otp == user_otp:
        del otp_storage[email]; return jsonify({'message': 'Login successful!'}), 200
    else: return jsonify({'error': 'Invalid or expired OTP'}), 401

@app.route('/analyze-url', methods=['POST'])
def analyze_url():
    if not API_KEY: return jsonify({'error': 'Server is missing YouTube API Key configuration.'}), 500
    data = request.get_json()
    if not data or 'url' not in data: return jsonify({'error': 'URL is required'}), 400
    video_id = get_video_id_from_url(data['url'])
    if not video_id: return jsonify({'error': 'Invalid YouTube URL provided'}), 400
    try:
        youtube = build("youtube", "v3", developerKey=API_KEY)
        video_response = youtube.videos().list(part="snippet,contentDetails,statistics", id=video_id).execute()
        if not video_response.get('items'): return jsonify({'error': 'Video not found or API request failed'}), 404
        item = video_response['items'][0]; snippet = item.get('snippet', {}); stats = item.get('statistics', {}); content = item.get('contentDetails', {})
        model_features = {}
        model_features['log_view_count'] = np.log1p(float(stats.get('viewCount', 0)))
        model_features['video_duration_sec'] = float(parse_iso8601_duration(content.get('duration', 'PT0S')))
        model_features['title_word_count'] = len(snippet.get('title', '').split())
        published_at_str = snippet.get('publishedAt')
        if published_at_str:
            dt_obj = datetime.fromisoformat(published_at_str.replace('Z', '+00:00'))
            model_features["publish_year"] = dt_obj.year; model_features["publish_month"] = dt_obj.month
            model_features["publish_dayofweek"] = dt_obj.weekday(); model_features["is_weekend"] = 1 if dt_obj.weekday() >= 5 else 0
        else: model_features.update({"publish_year": 0, "publish_month": 0, "publish_dayofweek": 0, "is_weekend": 0})
        response_data = { 'video_title': snippet.get('title', 'N/A'), 'channel_name': snippet.get('channelTitle', 'N/A'), **model_features }
        print(f"✅ Analyzed URL, returning features: {response_data}"); return jsonify(response_data), 200
    except HttpError as e: print(f"❌ YouTube API HTTP error: {e}"); return jsonify({'error': f'An HTTP error {e.resp.status} occurred.'}), 500
    except Exception as e: print(f"❌ Unexpected error in /analyze-url: {e}"); return jsonify({'error': 'An internal server error occurred.'}), 500

@app.route('/predict', methods=['POST'])
def predict():
    if not cat_model: return jsonify({'error': 'Model is not loaded, cannot make prediction.'}), 500
    data = request.get_json()
    if not data: return jsonify({'error': 'No data provided for prediction.'}), 400
    data['key_dopamine_factor'] = dopamine_factor_map.get(str(data.get('key_dopamine_factor', '')).lower(), 'No Dominant Factor')
    data['dominant_color'] = dominant_color_map.get(str(data.get('dominant_color', '')).lower(), 'No Dominant Color')
    data['video_category'] = video_category_map.get(str(data.get('video_category', '')).lower(), 'Missing')
    data['freq_cut_per_video'] = int(data.get('freq_cut_per_video', 0)); data['is_for_kids'] = int(data.get('is_for_kids', 0))
    try:
        user_df = pd.DataFrame([data]); final_cols = cat_model.feature_names_; user_df_final = user_df.reindex(columns=final_cols)
        for col in user_df_final.columns:
            if user_df_final[col].dtype == 'object': user_df_final[col].fillna('Missing', inplace=True)
            else: user_df_final[col].fillna(0, inplace=True)
        proba = cat_model.predict_proba(user_df_final)[0]; prediction_label_index = np.argmax(proba)
        final_label = f"{'High' if prediction_label_index == 1 else 'Low'} Dopamine"
        response = { 'probability_low': proba[0], 'probability_high': proba[1], 'final_label': final_label }
        print(f"✅ Prediction successful: {response}"); return jsonify(response)
    except Exception as e: print(f"❌ Error during prediction: {e}"); return jsonify({'error': 'Failed to process prediction.'}), 500

if __name__ == '__main__':
    # Added helper to run async code within Flask
    from helper import anext
    app.run(debug=True, port=5000)

