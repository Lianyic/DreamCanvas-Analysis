import os 
import redis
import openai
import requests
from flask import Flask, render_template, request, jsonify, redirect, Blueprint
from flask_cors import CORS
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# ==========================
# Configuration
# ==========================

load_dotenv()

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.getenv("SECRET_KEY", "79515e01fd5fe2ccf7abaa36bbea4640")

CORS(app, supports_credentials=True)

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "mysql+pymysql://adminuser:LeilaLily?!@dreamanalysis.mysql.database.azure.com/dream_analysis_db"
).strip('"')
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class DreamRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    dream_title = db.Column(db.String(255), nullable=False)
    dream_content = db.Column(db.Text, nullable=False)
    analysis_result = db.Column(db.Text, nullable=False)
    dream_date = db.Column(db.Date, nullable=True)
    image_url = db.Column(db.String(512), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

redis_client = redis.StrictRedis(
    host=os.getenv("REDIS_HOST", "dreamcanvas-redis.redis.cache.windows.net"),
    port=int(os.getenv("REDIS_PORT", 6380)),
    password=os.getenv("REDIS_PASSWORD"),
    ssl=True,
    decode_responses=True
)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=OPENAI_API_KEY)

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

bp = Blueprint("main", __name__)

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://dreamcanvas-auth.ukwest.azurecontainer.io:5000/")

# ==========================
# Helper Functions
# ==========================
def get_spotify_token():
    auth_url = "https://accounts.spotify.com/api/token"
    auth_response = requests.post(
        auth_url,
        data={"grant_type": "client_credentials"},
        auth=(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET),
    )

    if auth_response.status_code == 200:
        return auth_response.json().get("access_token")
    else:
        print("Spotify Auth Failed:", auth_response.json())
        return None

def get_spotify_recommendation(dream_mood):
    auth_url = "https://accounts.spotify.com/api/token"
    auth_response = requests.post(
        auth_url,
        data={"grant_type": "client_credentials"},
        auth=(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
    )

    auth_data = auth_response.json()
    access_token = auth_data.get("access_token")

    if not access_token:
        raise ValueError(f"Spotify Authentication Failed: {auth_data}")

    headers = {"Authorization": f"Bearer {access_token}"}
    search_url = f"https://api.spotify.com/v1/search?q={dream_mood}&type=playlist&limit=1"
    response = requests.get(search_url, headers=headers)

    data = response.json()
    playlists = data.get("playlists", {}).get("items", [])
    
    if not playlists:
        raise ValueError(f"No Spotify playlist found for mood: {dream_mood}")

    return playlists[0]["external_urls"]["spotify"]

# ==========================
# Routes
# ==========================

@bp.route("/")
def home():
    all_sessions = redis_client.keys("session:*")
    print("Available sessions in Redis:", all_sessions)

    if all_sessions:
        for session_key in all_sessions:
            username = session_key.split("session:")[-1]
            session_data = redis_client.get(session_key)
            if session_data:
                print(f"Found valid session for user: {username}")
                return redirect("http://dreamcanvas-analysis.ukwest.azurecontainer.io:5001/record")

    print(" No active sessions found. Redirecting to login.")
    return redirect(f"{AUTH_SERVICE_URL}/")

@bp.route("/record", methods=["GET"])
def record_page():
    
    all_sessions = redis_client.keys("session:*")
    print("Checking Redis for active sessions:", all_sessions)

    if not all_sessions:
        print("No active sessions, redirecting to login.")
        return redirect(AUTH_SERVICE_URL)

    for session_key in all_sessions:
        username = session_key.split("session:")[-1]
        session_data = redis_client.get(session_key)
        print(f"🔹 Checking session for {username}: {session_data}")

        if session_data:
            return render_template("record.html")

    print("No valid session found. Redirecting to login.")
    return redirect(AUTH_SERVICE_URL)

@bp.route("/analyze", methods=["POST"])
def analyze():
    all_sessions = redis_client.keys("session:*")

    if not all_sessions:
        return jsonify({"error": "Unauthorized access."}), 401

    data = request.json
    dream_date = data.get("date", "")
    user_input = data.get("text", "").strip()
    dream_type = data.get("type", "")
    dream_characters = data.get("characters", "")
    dream_environment = data.get("environment", "")
    dream_emotion = data.get("emotion", "")

    if not user_input:
        return jsonify({"error": "No text provided"}), 400

    
    prompt = f"""
    You are a professional dream analyst with deep expertise in psychology. Your task is to analyze the given dream in a natural, fluid, and engaging manner.

    Key Instructions:
    1. Provide a flowing and insightful analysis that captures the subconscious messages behind the dream, its potential connections to the dreamer's waking life, and its emotional significance.
    2. Assign a meaningful and concise dream title that captures its essence on the first line.
    3. Avoid breaking down the dream into rigid categories (e.g., "Main Theme:", "Dream Type:"). Instead, integrate the details seamlessly into a narrative.
    4. Suggest practical takeaways or small pieces of advice based on the dream interpretation.
    5. Limit the response to 200 words.

    Dream Description:
    Narrative: {user_input}
    Type of Dream: {dream_type}
    Key Characters: {dream_characters}
    Environment: {dream_environment}
    Emotion upon Waking: {dream_emotion}

    Deliverables:
    1. A short but meaningful dream title that summarizes its essence on the first line.
    2. A smooth, engaging psychological interpretation of the dream.
    3. A few thoughtful suggestions based on the interpretation, which may help the dreamer reflect on its meaning or apply insights to real life.
    """
    
    dalle_prompt = f"""
    Create a high-quality, minimalist, animated-style illustration that directly represents the underlying dream content.
    - Dream Content: {user_input}
    - Key Characters: {dream_characters}
    - Environment: {dream_environment}
    - Mood & Emotion: {dream_emotion}
    The style should resemble high-quality animation, using soft, dreamy color palettes.
    Avoid cluttered or overly complex details. Avoid words, logos, or any text in the image.
    The illustration should have soft lighting, smooth gradients, and a surreal but clean aesthetic.
    """

    try:
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert in dream interpretation."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.7
        )

        full_analysis = response.choices[0].message.content.strip()

        
        analysis_lines = full_analysis.split("\n", 1)
        dream_title = analysis_lines[0].strip()
        analysis_body = analysis_lines[1].strip() if len(analysis_lines) > 1 else "No analysis available."


        dalle_response = client.images.generate(
            model="dall-e-3",
            prompt=dalle_prompt,
            size="1024x1024",
            n=1
        )

        image_url = dalle_response.data[0].url if dalle_response.data else None

        
        playlist_url = get_spotify_recommendation(dream_emotion)

        
        for session_key in all_sessions:
            username = session_key.split("session:")[-1]
            session_data = redis_client.get(session_key)
            if session_data:
                new_record = DreamRecord(
                    username=username,
                    dream_title=dream_title,
                    dream_content=user_input,
                    analysis_result=analysis_body,
                    dream_date=dream_date,
                    image_url=image_url
                )
                db.session.add(new_record)
                db.session.commit()
                break

        return jsonify({
            "title": dream_title,
            "analysis": analysis_body,
            "image_url": image_url,
            "playlist_url": playlist_url
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==========================
# App Initialization
# ==========================

app.register_blueprint(bp)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)