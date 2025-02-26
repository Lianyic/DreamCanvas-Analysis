import os 
import redis
import openai
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
    dream_content = db.Column(db.Text, nullable=False)
    analysis_result = db.Column(db.Text, nullable=False)
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

bp = Blueprint("main", __name__)

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://dreamcanvas-auth.ukwest.azurecontainer.io:5000/")

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
def analyze_text():
    
    all_sessions = redis_client.keys("session:*")

    if not all_sessions:
        return jsonify({"error": "Unauthorized access."}), 401

    data = request.json
    user_input = data.get("text", "").strip()
    dream_theme = data.get("theme", "")
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
    2. Avoid breaking down the dream into rigid categories (e.g., "Main Theme:", "Dream Type:"). Instead, integrate the details seamlessly into a narrative.
    3. Suggest practical takeaways or small pieces of advice based on the dream interpretation.
    4. Assign a meaningful and concise dream title that captures its essence for easy reference in future dream logs.
    
    Dream Description:
    Narrative: {user_input}
    Main Theme: {dream_theme}
    Type of Dream: {dream_type}
    Key Characters: {dream_characters}
    Environment: {dream_environment}
    Emotion upon Waking: {dream_emotion}
    
    Deliverables:
    1. A short but meaningful dream title that summarizes its essence. (without "Dream Title:" or quatation marks in the response)
    2. A smooth, engaging psychological interpretation of the dream.
    3. A few thoughtful suggestions based on the interpretation, which may help the dreamer reflect on its meaning or apply insights to real life.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert in dream interpretation."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        analysis_result = response.choices[0].message.content.strip()

        for session_key in all_sessions:
            username = session_key.split("session:")[-1]
            session_data = redis_client.get(session_key)
            if session_data:
                new_record = DreamRecord(
                    username=username,
                    dream_content=user_input,
                    analysis_result=analysis_result
                )
                db.session.add(new_record)
                db.session.commit()
                break

        return jsonify({"analysis": analysis_result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==========================
# App Initialization
# ==========================

app.register_blueprint(bp)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)