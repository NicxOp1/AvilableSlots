from fastapi import FastAPI, Request, Body
from pydantic import BaseModel
from datetime import datetime, timedelta
import json

app = FastAPI()


class ScheduleData(BaseModel):
    possible_times: list[str]
    start: list[str]
    end: list[str]


@app.post("/schedule")
async def schedule_endpoint(request: Request,
                            data: list[ScheduleData] = Body(...)):
    # Hardcoded values
    overlap_threshold = 1
    slot_duration = "01:00"

    # Extract the data from the request body
    body = await request.json()

    # Process the data (you can use the logic from your existing file)
    available_times = body[0]["possible_times"]
    # Initialize lists to store all busy start and end times
    busy_start_times = []
    busy_end_times = []
    # Iterate through each schedule data
    for schedule in body:
        busy_start_times.extend(schedule["start"])
        busy_end_times.extend(schedule["end"])

    print(f"available_times: {available_times}")
    print(f"busy_start_times: {busy_start_times}")
    print(f"busy_end_times: {busy_end_times}")

    # Convert busy times to datetime objects
    busy_start_times = [
        datetime.strptime(time, "%Y-%m-%d %H:%M") for time in busy_start_times
    ]
    busy_end_times = [
        datetime.strptime(time, "%Y-%m-%d %H:%M") for time in busy_end_times
    ]

    # Function to check for overlap
    def count_overlaps(slot_start, slot_end):
        overlap_count = 0
        for busy_start, busy_end in zip(busy_start_times, busy_end_times):
            # Check if the slot overlaps with any busy time
            if slot_start < busy_end and slot_end > busy_start:
                overlap_count += 1
        return overlap_count

    # Get the current date
    current_date = datetime.now().strftime("%Y-%m-%d")

    # Convert available times to datetime
    available_times_dt = [
        datetime.strptime(f"{current_date} {t}", "%Y-%m-%d %H:%M")
        for t in available_times
    ]
    # Prioritize times ending in ":00", then ":30", then ":15"
    priority_order = {":00": 1, ":30": 2, ":15": 3, ":45": 4}
    sorted_times = sorted(available_times_dt,
                          key=lambda t: priority_order[t.strftime(":%M")])
    # Calculate overlap for each slot
    slot_overlaps = {}
    for slot_start in sorted_times:
        slot_end = slot_start + timedelta(
            hours=int(slot_duration.split(":")[0]),
            minutes=int(slot_duration.split(":")[1]))
        overlap_count = count_overlaps(slot_start, slot_end)
        slot_overlaps[slot_start.strftime("%H:%M")] = overlap_count

    print(f"slot_overlaps: {slot_overlaps}")

    # Filter out slots with overlap greater than 1
    filtered_slots = [slot for slot, overlap in slot_overlaps.items() if overlap <= overlap_threshold]
    # Sort the filtered slots by time
    sorted_slots = sorted(filtered_slots, key=lambda item: priority_order[f":{item.split(':')[1]}"])
    valid_slots = sorted_slots[:2]

    print(f"sorted_slots: {sorted_slots}")
    print(f"valid_slots: {valid_slots}")

    # Format the response
    if valid_slots:
        response = f'The first two available time slots are: {valid_slots}.'
    else:
        response = 'There are no available time slots. Could you please suggest another day?'
    return {"message": response}


# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)