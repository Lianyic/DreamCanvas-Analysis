import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, Blueprint
from flask_cors import CORS
import openai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.getenv("SECRET_KEY")

CORS(app, supports_credentials=True)

app.config.update(
    SESSION_COOKIE_SAMESITE="None", 
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_NAME="session",
    SESSION_COOKIE_DOMAIN=None
)

# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Blueprint for routes
bp = Blueprint("main", __name__)

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://dreamcanvas-auth.ukwest.azurecontainer.io:5000/")

@bp.route("/")
def home():
    app.logger.info("Session Data:", session)
    if "username" in session:
        redirect("http://dreamcanvas-analysis.ukwest.azurecontainer.io:5001/record")
    return redirect(f"{AUTH_SERVICE_URL}/")

@bp.route("/record", methods=["GET"])
def record_page():
    app.logger.info("Session Data:", session)
    app.logger.info("Cookies Received:", request.cookies)

    if "username" not in session:
        app.logger.info("No username in session, redirecting to home...")
        print("No username in session, redirecting to home...")
        return redirect("http://dreamcanvas-auth.ukwest.azurecontainer.io:5000/")

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

        analysis = response.choices[0].message.content.strip()
        return jsonify({"analysis": analysis})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.after_request
def apply_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "http://dreamcanvas-auth.ukwest.azurecontainer.io:5000"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

app.register_blueprint(bp)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)