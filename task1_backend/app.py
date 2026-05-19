# ============================================================
# TASK 1: Task Management System - REST API
# Built with Flask + SQLite
# Author:  Toheeb Olanrewaju Olagoke   Intern ID: RDXINTTOHEWH86E
# ============================================================

from flask import Flask, request, jsonify
from database import init_db, get_db_connection
import sqlite3

# Create the Flask app
app = Flask(__name__)

# Initialize the database when the app starts
init_db()


# ─────────────────────────────────────────
# VALIDATION HELPERS
# ─────────────────────────────────────────
def validate_task(data):
    errors = []
    if not data.get("title") or data["title"].strip() == "":
        errors.append("Title is required and cannot be empty.")
    if not data.get("user_id"):
        errors.append("user_id is required.")
    if "status" in data and data["status"] not in ["pending", "in_progress", "completed"]:
        errors.append("Status must be one of: pending, in_progress, completed.")
    return errors


def validate_user(data):
    errors = []
    if not data.get("name") or not data["name"].strip():
        errors.append("Name is required.")
    if not data.get("email") or "@" not in data.get("email", ""):
        errors.append("A valid email is required.")
    return errors


# ═════════════════════════════════════════
# TASK ROUTES
# ═════════════════════════════════════════

# ROUTE 1: GET /tasks - Get all tasks
@app.route("/tasks", methods=["GET"])
def get_tasks():
    try:
        conn = get_db_connection()
        tasks = conn.execute("SELECT * FROM tasks").fetchall()
        conn.close()
        task_list = [dict(t) for t in tasks]
        return jsonify({"success": True, "tasks": task_list, "count": len(task_list)}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ROUTE 2: GET /tasks/<id> - Get one task
@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    try:
        conn = get_db_connection()
        task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        conn.close()
        if task is None:
            return jsonify({"success": False, "error": f"Task with ID {task_id} not found."}), 404
        return jsonify({"success": True, "task": dict(task)}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ROUTE 3: POST /tasks - Create a new task
@app.route("/tasks", methods=["POST"])
def create_task():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Request body must be JSON."}), 400

        errors = validate_task(data)
        if errors:
            return jsonify({"success": False, "errors": errors}), 400

        title = data["title"].strip()
        description = data.get("description", "").strip()
        status = data.get("status", "pending")
        user_id = data["user_id"]

        conn = get_db_connection()

        # Check the user exists before inserting (proves the relationship)
        user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if user is None:
            conn.close()
            return jsonify({"success": False, "error": f"User with ID {user_id} not found."}), 404

        cursor = conn.execute(
            "INSERT INTO tasks (title, description, status, user_id) VALUES (?, ?, ?, ?)",
            (title, description, status, user_id)
        )
        conn.commit()
        new_id = cursor.lastrowid

        task = conn.execute("SELECT * FROM tasks WHERE id = ?", (new_id,)).fetchone()
        conn.close()

        return jsonify({"success": True, "message": "Task created!", "task": dict(task)}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ROUTE 4: PUT /tasks/<id> - Update a task
@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    try:
        conn = get_db_connection()
        task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()

        if task is None:
            conn.close()
            return jsonify({"success": False, "error": f"Task with ID {task_id} not found."}), 404

        data = request.get_json()
        if not data:
            conn.close()
            return jsonify({"success": False, "error": "Request body must be JSON."}), 400

        # Validate status if provided
        if "status" in data and data["status"] not in ["pending", "in_progress", "completed"]:
            conn.close()
            return jsonify({
                "success": False,
                "errors": ["Status must be one of: pending, in_progress, completed."]
            }), 400

        # Partial update: keep existing values when none provided
        title = data.get("title", task["title"])
        description = data.get("description", task["description"])
        status = data.get("status", task["status"])

        conn.execute(
            "UPDATE tasks SET title = ?, description = ?, status = ? WHERE id = ?",
            (title, description, status, task_id)
        )
        conn.commit()

        updated_task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        conn.close()

        return jsonify({"success": True, "message": "Task updated!", "task": dict(updated_task)}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ROUTE 5: DELETE /tasks/<id> - Delete a task
@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    try:
        conn = get_db_connection()
        task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()

        if task is None:
            conn.close()
            return jsonify({"success": False, "error": f"Task with ID {task_id} not found."}), 404

        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()

        return jsonify({"success": True, "message": f"Task {task_id} deleted successfully."}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ═════════════════════════════════════════
# USER ROUTES (relationship: one user → many tasks)
# ═════════════════════════════════════════

# ROUTE 6: POST /users - Create a user
@app.route("/users", methods=["POST"])
def create_user():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Request body must be JSON."}), 400

        errors = validate_user(data)
        if errors:
            return jsonify({"success": False, "errors": errors}), 400

        conn = get_db_connection()
        try:
            cursor = conn.execute(
                "INSERT INTO users (name, email) VALUES (?, ?)",
                (data["name"].strip(), data["email"].strip())
            )
            conn.commit()
            user = conn.execute("SELECT * FROM users WHERE id = ?", (cursor.lastrowid,)).fetchone()
        except sqlite3.IntegrityError:
            conn.close()
            return jsonify({"success": False, "error": "Email already exists."}), 400

        conn.close()
        return jsonify({"success": True, "message": "User created!", "user": dict(user)}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ROUTE 7: GET /users - Get all users
@app.route("/users", methods=["GET"])
def get_users():
    try:
        conn = get_db_connection()
        users = conn.execute("SELECT * FROM users").fetchall()
        conn.close()
        return jsonify({"success": True, "users": [dict(u) for u in users], "count": len(users)}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ROUTE 8: GET /users/<id>/tasks - Get all tasks for a user (RELATIONSHIP)
@app.route("/users/<int:user_id>/tasks", methods=["GET"])
def get_user_tasks(user_id):
    try:
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if user is None:
            conn.close()
            return jsonify({"success": False, "error": "User not found."}), 404

        tasks = conn.execute("SELECT * FROM tasks WHERE user_id = ?", (user_id,)).fetchall()
        conn.close()
        return jsonify({
            "success": True,
            "user": dict(user),
            "tasks": [dict(t) for t in tasks],
            "count": len(tasks)
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ═════════════════════════════════════════
# HOME ROUTE
# ═════════════════════════════════════════
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Welcome to the Task Management API!",
        "endpoints": {
            "GET /tasks": "Get all tasks",
            "GET /tasks/<id>": "Get one task",
            "POST /tasks": "Create a task",
            "PUT /tasks/<id>": "Update a task",
            "DELETE /tasks/<id>": "Delete a task",
            "POST /users": "Create a user",
            "GET /users": "Get all users",
            "GET /users/<id>/tasks": "Get all tasks for a user"
        }
    }), 200


# ═════════════════════════════════════════
# RUN THE APP
# ═════════════════════════════════════════
if __name__ == "__main__":
    print("🚀 Task Management API is running at http://127.0.0.1:5000")
    app.run(debug=True)