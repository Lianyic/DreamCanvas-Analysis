import os
from flask import Flask, render_template, request, jsonify, redirect, session, Blueprint
from flask_cors import CORS
from flask_session import Session
import redis
import openai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.getenv("SECRET_KEY", "79515e01fd5fe2ccf7abaa36bbea4640")

CORS(app, supports_credentials=True)


app.config["SESSION_TYPE"] = "redis"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_USE_SIGNER"] = True
app.config["SESSION_KEY_PREFIX"] = "session:"
app.config["SESSION_REDIS"] = redis.StrictRedis(
    host=os.getenv("REDIS_HOST", "dreamcanvas-redis.redis.cache.windows.net"),
    port=int(os.getenv("REDIS_PORT", 6380)),
    password=os.getenv("REDIS_PASSWORD"),
    ssl=True,
    decode_responses=True
)


Session(app)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=OPENAI_API_KEY)

bp = Blueprint("main", __name__)

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://dreamcanvas-auth.ukwest.azurecontainer.io:5000/")

@bp.route("/")
def home():
    if "username" in session:
        return redirect("http://dreamcanvas-analysis.ukwest.azurecontainer.io:5001/record")
    return redirect(f"{AUTH_SERVICE_URL}/")

@bp.route("/record", methods=["GET"])
def record_page():
    if "username" not in session:
        return redirect(AUTH_SERVICE_URL)
    return render_template("record.html")

@bp.route("/analyze", methods=["POST"])
def analyze_text():
    if "username" not in session:
        return jsonify({"error": "Unauthorized access."}), 401

    data = request.json
    user_input = data.get("text", "")

    if not user_input:
        return jsonify({"error": "No text provided"}), 400

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a professional psychologist with expertise in dream analysis."},
                {"role": "user", "content": f"Analyze this dream: {user_input}"}
            ],
            max_tokens=500,
            temperature=0.7
        )
        return jsonify({"analysis": response.choices[0].message.content.strip()})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

app.register_blueprint(bp)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)