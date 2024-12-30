import requests
import random
import time
from datetime import datetime, timedelta

# API URL
API_URL = "https://winter-intern-task.onrender.com/slot/add"

# Users
USERS = [ "Lorem"]

# Helper to generate a random time between 8:00 AM and 10:00 PM
def get_random_time(used_times):
    while True:
        start_time = datetime(2024, 12, 23, 8, 0)
        end_time = datetime(2024, 12, 23, 22, 0)
        random_time = start_time + timedelta(minutes=random.randint(0, (end_time - start_time).seconds // 60 // 30) * 30)
        if random_time.time() not in used_times:
            used_times.add(random_time.time())
            return random_time.time()

# Function to send a single POST request
def send_post_request(user_id, date, start_time, end_time):
    data = {
        "user_id": user_id,
        "date": date,
        "slot": {
            "start_time": start_time,
            "end_time": end_time
        }
    }
    try:
        response = requests.post(API_URL, json=data, headers={"Content-Type": "application/json"})
        if response.status_code == 200:
            print(f"Success for {user_id}: {response.json()}")
        else:
            print(f"Failed for {user_id}: {response.status_code} {response.text}")
    except Exception as e:
        print(f"Error for {user_id}: {e}") 
        

# Function to populate slots for a specific day
def populate_slots_for_day(date, num_slots):
    used_times = set()  # Keep track of used times for the day
    for _ in range(num_slots):
        user_id = random.choice(USERS)  # Randomly select a user
        start_time = get_random_time(used_times)
        end_time = (datetime.combine(datetime.today(), start_time) + timedelta(minutes=30)).time()
        send_post_request(user_id, date, start_time.isoformat(), end_time.isoformat())

# Function to populate the database
def populate_database():
    start_date = datetime(2024, 12, 20)
    end_date = datetime(2025, 2, 10)
    delay_seconds = 1

    current_date = start_date
    while current_date <= end_date:
        # Decide the number of slots for the day
        num_slots = random.choices(
            [0, random.randint(1, 6), random.randint(7, 13), random.randint(14, 20)],
            weights=[0.1, 0.3, 0.4, 0.2]
        )[0]

        if num_slots > 0:
            print(f"Adding {num_slots} slots for {current_date.date()}")
            populate_slots_for_day(current_date.date().isoformat(), num_slots)
            time.sleep(delay_seconds)

        # Move to the next day
        current_date += timedelta(days=1)

# Run the script
if __name__ == "__main__":
    populate_database()
