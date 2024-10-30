import psycopg2
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Connect to Supabase PostgreSQL database
DATABASE_URL = os.getenv("DATABASE_URL")
try:
    conn = psycopg2.connect(DATABASE_URL)
    print("Database connected successfully!")
except Exception as e:
    print(f"Error connecting to database: {e}")

@app.route("/", methods=["GET"])
def home():
    """Root route to prevent 404 errors."""
    return jsonify({"message": "Welcome to the Smart To-Do Backend API!"}), 200

@app.route("/tasks", methods=["GET"])
def get_tasks():
    """Fetch all tasks for a specific user."""
    user_id = request.args.get('user_id')  # User ID passed as a query parameter
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, task_name, completed FROM tasks WHERE user_id = %s", 
            (user_id,)
        )
        tasks = cur.fetchall()
        cur.close()
        return jsonify(tasks), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/tasks", methods=["POST"])
def create_task():
    """Create a new task for a specific user."""
    data = request.json
    user_id = data.get('user_id')
    task_name = data.get('task_name')

    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO tasks (user_id, task_name) VALUES (%s, %s) RETURNING id",
            (user_id, task_name)
        )
        new_task_id = cur.fetchone()[0]
        conn.commit()
        cur.close()

        return jsonify({"id": new_task_id, "task_name": task_name, "completed": False}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health_check():
    """Health check route to verify if the server is running."""
    return jsonify({"status": "OK"}), 200

if __name__ == "__main__":
    # Ensure the app listens on port 5000 for Render compatibility
    app.run(host="0.0.0.0", port=5000)
