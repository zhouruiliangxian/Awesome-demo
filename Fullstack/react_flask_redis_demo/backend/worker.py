
import redis
import time
import ast

# Connect to our Redis instance
redis_client = redis.Redis(host='localhost', port=6380, db=0, decode_responses=True)

print("Worker started. Waiting for tasks...")

while True:
    try:
        # 1. Wait for a task to appear in the queue
        # BRPOP is a blocking command, it will wait until a task is available
        _, task_string = redis_client.brpop('tasks:queue')

        # Convert the string representation of the dictionary back to a dictionary
        task_data = ast.literal_eval(task_string)
        task_id = task_data.get('id')

        if not task_id:
            print("Skipping invalid task data.")
            continue

        print(f"Processing task {task_id}...")

        # 2. Update task status to 'processing'
        redis_client.hset(f"task_status:{task_id}", "status", "processing")
        redis_client.hset(f"task_status:{task_id}", "message", "Task is being processed.")

        # 3. Simulate a long-running task
        time.sleep(10)

        # 4. Update task status to 'completed'
        redis_client.hset(f"task_status:{task_id}", "status", "completed")
        redis_client.hset(f"task_status:{task_id}", "message", f"Task {task_id} completed successfully!")

        print(f"Task {task_id} finished.")

    except Exception as e:
        print(f"An error occurred: {e}")
        time.sleep(5) # Wait a bit before retrying
