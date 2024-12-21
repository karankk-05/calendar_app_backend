import os
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import date, time
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Fetch MongoDB credentials from environment variables
mongo_password = os.getenv("MONGO_DB_PASSWORD")
mongo_user = os.getenv("MONGO_DB_USER")
mongo_cluster = os.getenv("MONGO_DB_CLUSTER")

# Build the MongoDB URI
mongo_uri = f"mongodb+srv://{mongo_user}:{mongo_password}@{mongo_cluster}/?retryWrites=true&w=majority"

# Initialize MongoDB client using the URI
client = MongoClient(mongo_uri)
db = client.calendar_db
slots_collection = db.slots

# Initialize FastAPI app
app = FastAPI()

# Pydantic models
class Slot(BaseModel):
    start_time: time
    end_time: time

class DaySlots(BaseModel):
    date: date
    slots: List[Slot]

class SlotsResponse(BaseModel):
    date: date
    total_slots: int
    available_slots: int
    slots: List[Slot]

class AddUpdateSlotRequest(BaseModel):
    user_id: str
    date: date
    slot: Slot

class RemoveSlotRequest(BaseModel):
    user_id: str
    date: date
    slot: Slot

# Helper functions
def fetch_slots(user_id: str, start_date: date, end_date: Optional[date] = None):
    # Convert dates to datetime for MongoDB compatibility
    start_datetime = datetime.combine(start_date, datetime.min.time())
    query = {"user_id": user_id, "date": {"$gte": start_datetime}}

    if end_date:
        end_datetime = datetime.combine(end_date, datetime.min.time())
        query["date"]["$lte"] = end_datetime

    # Query MongoDB
    results = list(slots_collection.find(query))
    return [
        {
            "date": res["date"].date(),  # Convert datetime back to date
            "total_slots": 20,          # Assuming a total of 20 slots per day
            "available_slots": 20 - len(res.get("slots", [])),
            "slots": [
                {
                    "start_time": time.fromisoformat(slot["start_time"]),
                    "end_time": time.fromisoformat(slot["end_time"]),
                }
                for slot in res.get("slots", [])
            ],
        }
        for res in results
    ]

# Routes
@app.get("/slots", response_model=List[SlotsResponse])
def get_slots(user_id: str, start_date: date, end_date: Optional[date] = None):
    """Fetch slot availability for a user within a date range."""
    data = fetch_slots(user_id, start_date, end_date)
    if not data:
        raise HTTPException(status_code=404, detail="No data found for the given range.")
    return data

@app.post("/slot/add")
def add_slot(request: AddUpdateSlotRequest):
    # Convert date to a datetime object
    date_as_datetime = datetime.combine(request.date, datetime.min.time())

    # Convert slot times to string for storage
    slot_data = {
        "start_time": request.slot.start_time.isoformat(),
        "end_time": request.slot.end_time.isoformat(),
    }
    
    # Check if the slot already exists
    existing_slot_data = slots_collection.find_one({"user_id": request.user_id, "date": date_as_datetime})
    
    if existing_slot_data:
        # Check for overlapping slots
        for slot in existing_slot_data["slots"]:
            if slot["start_time"] == slot_data["start_time"] and slot["end_time"] == slot_data["end_time"]:
                raise HTTPException(status_code=400, detail="Slot already exists!")
        
        # Add new slot
        slots_collection.update_one(
            {"user_id": request.user_id, "date": date_as_datetime},
            {"$push": {"slots": slot_data}}
        )
    else:
        # Insert a new record
        slots_collection.insert_one({
            "user_id": request.user_id,
            "date": date_as_datetime,
            "slots": [slot_data]
        })
    return {"message": "Slot added successfully!"}

@app.put("/slot/update")
def update_slot(request: AddUpdateSlotRequest):
    """Update slot details for a specific user and date."""
    slot_data = slots_collection.find_one({"user_id": request.user_id, "date": request.date})

    if not slot_data:
        raise HTTPException(status_code=404, detail="Slot data not found for the given date.")

    updated_slot = {"start_time": str(request.slot.start_time), "end_time": str(request.slot.end_time)}

    slots_collection.update_one(
        {"_id": slot_data["_id"], "slots.start_time": str(request.slot.start_time)},
        {"$set": {"slots.$": updated_slot}}
    )
    return {"message": "Slot updated successfully."}

@app.delete("/slot/remove")
def remove_slot(request: RemoveSlotRequest):
    """Remove a slot for a specific user and date."""
    slot_data = slots_collection.find_one({"user_id": request.user_id, "date": request.date})

    if not slot_data:
        raise HTTPException(status_code=404, detail="Slot data not found for the given date.")

    remove_slot = {"start_time": str(request.slot.start_time), "end_time": str(request.slot.end_time)}

    slots_collection.update_one(
        {"_id": slot_data["_id"]},
        {"$pull": {"slots": remove_slot}}
    )
    return {"message": "Slot removed successfully."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
