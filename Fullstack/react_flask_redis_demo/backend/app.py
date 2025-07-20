
from flask import Flask, jsonify, request
from flask_cors import CORS
import redis
import uuid

app = Flask(__name__)
CORS(app)  # Allow requests from the React frontend

# Connect to our Redis instance
# Make sure to use the correct port if you changed it
redis_client = redis.Redis(host='localhost', port=6380, db=0, decode_responses=True)

@app.route('/api/start-task', methods=['POST'])
def start_task():
    # 1. Generate a unique ID for the task
    task_id = str(uuid.uuid4())

    # 2. Create a task object (can be more complex)
    task_data = {
        "id": task_id,
        "message": "Starting a new background task..."
    }

    # 3. Push the task to the Redis queue (a list)
    redis_client.lpush('tasks:queue', str(task_data))

    # 4. Set the initial status in Redis (a hash)
    redis_client.hset(f"task_status:{task_id}", mapping={
        "status": "queued",
        "message": "Task is waiting in the queue."
    })

    # 5. Immediately return the task ID to the client
    return jsonify({"task_id": task_id}), 202

@app.route('/api/task-status/<task_id>', methods=['GET'])
def get_task_status(task_id):
    # Query Redis for the status of the given task ID
    status_data = redis_client.hgetall(f"task_status:{task_id}")

    if not status_data:
        return jsonify({"error": "Task not found"}), 404

    return jsonify(status_data)

if __name__ == '__main__':
    app.run(debug=True, port=5001) # Running on a different port than default 5000
