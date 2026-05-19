# Task Management API — Documentation

## Base URL
http://127.0.0.1:5000

---

## Endpoints

### 1. GET /tasks
Returns all tasks.

**Response:**
```json
{
  "success": true,
  "count": 2,
  "tasks": [
    { "id": 1, "title": "Buy groceries", "description": "", "status": "pending", "created_at": "..." },
    { "id": 2, "title": "Write report", "description": "Monthly report", "status": "completed", "created_at": "..." }
  ]
}
```

---

### 2. GET /tasks/<id>
Returns a single task by ID.

**Example:** GET /tasks/1

---

### 3. POST /tasks
Creates a new task.

**Request Body (JSON):**
```json
{
  "title": "Learn Flask",
  "description": "Complete the Flask tutorial",
  "status": "pending"
}
```
Status options: `pending` | `in_progress` | `completed`

---

### 4. PUT /tasks/<id>
Updates an existing task.

**Example:** PUT /tasks/1

**Request Body (JSON):**
```json
{
  "status": "completed"
}
```

---

### 5. DELETE /tasks/<id>
Deletes a task by ID.

**Example:** DELETE /tasks/1

---

## Status Codes
| Code | Meaning |
|------|---------|
| 200  | Success |
| 201  | Created |
| 400  | Bad Request (validation error) |
| 404  | Not Found |
| 500  | Server Error |
