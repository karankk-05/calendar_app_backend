# Calendar Application - Backend

FastAPI backend for slot management with MongoDB database.

## Key Features
- Slot CRUD operations with overlap prevention
- Date-range queries for slot availability
- Sample data population script

## API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/slots/total` | GET | Total/available slots in date range |
| `/slots/details` | GET | Detailed booked/available slots for specific date |
| `/slots` | GET | User availability in date range |
| `/slot/add` | POST | Add new slot (prevents overlaps) |
| `/slot/update` | POST | Update existing slot |
| `/slot/remove` | POST | Delete slot |

## Setup Instructions
```bash
# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn main:app --reload
