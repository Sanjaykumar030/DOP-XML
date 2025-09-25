import re
import warnings
from datetime import datetime
import os
from dotenv import load_dotenv
import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from flask import Flask, request, jsonify
from flask_cors import CORS
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import isodate
from flask_sqlalchemy import SQLAlchemy

# --- Suppress future warnings ---
warnings.filterwarnings("ignore", category=FutureWarning)

# === FLASK APP INITIALIZATION ===
load_dotenv()
app = Flask(__name__)
CORS(app)

# === DATABASE CONFIGURATION ===
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///predictions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# === DATABASE MODEL ===
class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    youtube_url = db.Column(db.String(200), nullable=False)
    video_title = db.Column(db.String(200), nullable=False)
    final_label = db.Column(db.String(50), nullable=False)
    probability_high = db.Column(db.Float, nullable=False)
    probability_low = db.Column(db.Float, nullable=False)
    prediction_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<Prediction {self.video_title}>'

# === CONFIGURATION ===
API_KEY = os.getenv("YOUTUBE_API_KEY")
MODEL_PATH = "catboost_dopamine_model.cbm"

if not API_KEY:
    print("❌ CRITICAL ERROR: 'YOUTUBE_API_KEY' not found in your .env file.")

try:
    cat_model = CatBoostClassifier()
    model_path = os.path.join(os.path.dirname(__file__), MODEL_PATH)
    cat_model.load_model(model_path)
    print(f"✅ CatBoost model loaded successfully from {model_path}.")
except Exception as e:
    print(f"❌ CRITICAL ERROR: Could not load model from '{model_path}'. Error: {e}")
    cat_model = None

# === DATA MAPPINGS ===
dopamine_factor_map = {
    "no dominant factor": "No Dominant Factor", "repetitive music/audio": "Repetitive Music/Audio",
    "catchy/melodic music": "Catchy/Melodic Music", "element of surprise": "Element of Surprise",
    "on-screen positive feedback": "On-screen Positive Feedback", "game-like progression": "Game-like Progression",
    "familiar characters": "Familiar Characters", "distinctive sound effects": "Distinctive Sound Effects",
    "engaging narrative": "Engaging Narrative", "visual effects": "Visual Effects",
    "unique animation style": "Unique Animation Style", "creative elements": "Creative Elements"
}
dominant_color_map = {
    "no dominant color": "No Dominant Color", "multi colors": "Multi Colors", "blue": "Blue", "pink": "Pink",
    "white": "White", "violet": "Violet", "peach": "Peach", "green": "Green", "red": "Red", "yellow": "Yellow",
    "orange": "Orange", "brown": "Brown", "black": "Black", "grey": "Grey", "purple": "Purple"
}
video_category_map = {
    "missing": "Missing", "advertisement": "Advertisement", "country vlog": "Country Vlog",
    "documentary": "Documentary", "education": "Education", "entertainment": "Entertainment",
    "food vlog": "Food Vlog", "gaming": "Gaming", "informative": "Informative",
    "inspiration": "Inspiration", "motivation": "Motivation", "music": "Music", "nature": "Nature",
    "nursery rhymes": "Nursery Rhymes", "short story": "Short Story", "shots": "Shots",
    "tourism": "Tourism", "travel vlog": "Travel Vlog", "vlog": "Vlog"
}

# === HELPER FUNCTIONS ===
def parse_iso8601_duration(duration_str):
    try:
        return int(isodate.parse_duration(duration_str).total_seconds())
    except:
        return 0

def get_video_id_from_url(url):
    match = (
        re.search(r"(?<=v=)[\w-]+", url) or
        re.search(r"(?<=be/)[\w-]+", url) or
        re.search(r"(?<=embed/)[\w-]+", url)
    )
    return match.group(0) if match else None

# === API ENDPOINTS ===
@app.route('/analyze-url', methods=['POST'])
def analyze_url():
    if not API_KEY:
        return jsonify({'error': 'Server is missing YouTube API Key configuration.'}), 500
        
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'URL is required'}), 400

    video_id = get_video_id_from_url(data['url'])
    if not video_id:
        return jsonify({'error': 'Invalid YouTube URL provided'}), 400

    try:
        youtube = build("youtube", "v3", developerKey=API_KEY)
        video_response = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=video_id
        ).execute()

        if not video_response.get('items'):
            return jsonify({'error': 'Video not found or API request failed'}), 404

        item = video_response['items'][0]
        snippet = item.get('snippet', {})
        stats = item.get('statistics', {})
        content = item.get('contentDetails', {})
        
        model_features = {}
        raw_view_count = float(stats.get('viewCount', 0))
        model_features['log_view_count'] = np.log1p(raw_view_count)
        model_features['video_duration_sec'] = float(parse_iso8601_duration(content.get('duration', 'PT0S')))
        model_features['title_word_count'] = len(snippet.get('title', '').split())

        published_at_str = snippet.get('publishedAt')
        if published_at_str:
            dt_obj = datetime.fromisoformat(published_at_str.replace('Z', '+00:00'))
            model_features["publish_year"] = dt_obj.year
            model_features["publish_month"] = dt_obj.month
            model_features["publish_dayofweek"] = dt_obj.weekday()
            model_features["is_weekend"] = 1 if dt_obj.weekday() >= 5 else 0
        else:
            model_features.update({"publish_year": 0, "publish_month": 0, "publish_dayofweek": 0, "is_weekend": 0})

        response_data = {
            'video_title': snippet.get('title', 'N/A'),
            'channel_name': snippet.get('channelTitle', 'N/A'),
            **model_features
        }
        
        print(f"✅ Analyzed URL, returning features: {response_data}")
        return jsonify(response_data), 200

    except HttpError as e:
        print(f"❌ YouTube API HTTP error: {e}")
        return jsonify({'error': f'An HTTP error {e.resp.status} occurred.'}), 500
    except Exception as e:
        print(f"❌ Unexpected error in /analyze-url: {e}")
        return jsonify({'error': 'An internal server error occurred.'}), 500

@app.route('/predict', methods=['POST'])
def predict():
    if not cat_model:
        return jsonify({'error': 'Model is not loaded, cannot make prediction.'}), 500
        
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided for prediction.'}), 400

    print(f"▶️ Received data for prediction: {data}")

    data['key_dopamine_factor'] = dopamine_factor_map.get(str(data.get('key_dopamine_factor', '')).lower(), 'No Dominant Factor')
    data['dominant_color'] = dominant_color_map.get(str(data.get('dominant_color', '')).lower(), 'No Dominant Color')
    data['video_category'] = video_category_map.get(str(data.get('video_category', '')).lower(), 'Missing')
    data['freq_cut_per_video'] = int(data.get('freq_cut_per_video', 0))
    data['is_for_kids'] = int(data.get('is_for_kids', 0))

    try:
        user_df = pd.DataFrame([data])
        
        final_cols = cat_model.feature_names_
        user_df_final = user_df.reindex(columns=final_cols)
        
        for col in user_df_final.columns:
            if user_df_final[col].dtype == 'object':
                user_df_final[col].fillna('Missing', inplace=True)
            else:
                user_df_final[col].fillna(0, inplace=True)

        proba = cat_model.predict_proba(user_df_final)[0]
        prediction_label_index = np.argmax(proba)
        
        final_label = f"{'High' if prediction_label_index == 1 else 'Low'} Dopamine"

        response = {
            'probability_low': proba[0],
            'probability_high': proba[1],
            'final_label': final_label
        }
        
        # === SAVE TO DATABASE ===
        new_prediction = Prediction(
            youtube_url=data.get('url', 'N/A'),
            video_title=data.get('video_title', 'N/A'),
            final_label=response['final_label'],
            probability_high=response['probability_high'],
            probability_low=response['probability_low']
        )
        db.session.add(new_prediction)
        db.session.commit()
        # ============================
        
        print(f"✅ Prediction successful and saved: {response}")
        return jsonify(response)

    except Exception as e:
        print(f"❌ Error during prediction: {e}")
        return jsonify({'error': 'Failed to process prediction.'}), 500

@app.route('/history', methods=['GET'])
def get_history():
    """Endpoint to fetch predictions, with sorting capability."""
    try:
        # Get sort order from query params, default to 'desc'
        sort_order = request.args.get('sort', 'desc').lower()

        # Build the query based on the sort order
        if sort_order == 'asc':
            query = Prediction.query.order_by(Prediction.prediction_date.asc())
        else:
            query = Prediction.query.order_by(Prediction.prediction_date.desc())
            
        predictions = query.all()
        
        # Convert prediction objects into a list of dictionaries
        history_list = []
        for p in predictions:
            history_list.append({
                'id': p.id,
                'youtube_url': p.youtube_url,
                'video_title': p.video_title,
                'final_label': p.final_label,
                'probability_high': p.probability_high,
                'probability_low': p.probability_low,
                'prediction_date': p.prediction_date.strftime('%Y-%m-%d %H:%M:%S')
            })
            
        return jsonify(history_list)

    except Exception as e:
        print(f"❌ Error fetching history: {e}")
        return jsonify({'error': 'Failed to fetch prediction history.'}), 500

@app.route('/history/<int:prediction_id>', methods=['DELETE'])
def delete_prediction(prediction_id):
    """Endpoint to delete a specific prediction from the history."""
    try:
        # Find the prediction by its ID
        prediction_to_delete = Prediction.query.get(prediction_id)

        # If the prediction doesn't exist, return a 404 error
        if not prediction_to_delete:
            return jsonify({'error': 'Prediction not found.'}), 404

        # Delete the prediction and commit the change
        db.session.delete(prediction_to_delete)
        db.session.commit()

        print(f"✅ Deleted prediction with ID: {prediction_id}")
        return jsonify({'message': 'Prediction deleted successfully.'}), 200

    except Exception as e:
        print(f"❌ Error deleting prediction: {e}")
        return jsonify({'error': 'Failed to delete prediction.'}), 500

# NEW: Endpoint to clear the entire prediction history
@app.route('/history', methods=['DELETE'])
def clear_history():
    """Endpoint to delete all predictions from the history."""
    try:
        # Efficiently delete all rows from the Prediction table
        num_rows_deleted = db.session.query(Prediction).delete()
        db.session.commit()

        print(f"✅ Cleared complete history. {num_rows_deleted} records deleted.")
        return jsonify({'message': f'All {num_rows_deleted} prediction(s) cleared successfully.'}), 200

    except Exception as e:
        # Rollback in case of error to keep the DB state consistent
        db.session.rollback() 
        print(f"❌ Error clearing history: {e}")
        return jsonify({'error': 'Failed to clear prediction history.'}), 500

if __name__ == '__main__':
    # Create the database and tables if they don't exist
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)