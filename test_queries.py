import sys
import os

# Append the database directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "database"))

from database.queries import (
    get_user,
    insert_event,
    update_event,
    delete_event,
    assign_student,
    insert_event_file,
    insert_feedback,
    save_uploaded_file,
    generate_next_event_id,
    generate_unique_file_id,
    generate_unique_feedback_id
)

def test_get_user():
    print("Testing: get_user")
    try:
        user = get_user("Alice", "alice@123", "Teacher")
        print("Result:", user)
    except Exception as e:
        print("Error in get_user:", e)

def test_insert_event():
    print("\nTesting: insert_event")
    try:
        event_id = insert_event("Math Olympiad", "2025-03-30", "10:00 AM", "01:00 PM", "Central Auditorium", "BSTEACH01")
        print("Event inserted successfully with ID:", event_id)
    except Exception as e:
        print("Error in insert_event:", e)

def test_update_event():
    print("\nTesting: update_event")
    try:
        update_event("EID01", "Updated School Anniversary", "2025-03-19", "10:00 AM", "01:00 PM", "Main Hall")
        print("Event updated successfully.")
    except Exception as e:
        print("Error in update_event:", e)

def test_delete_event():
    print("\nTesting: delete_event")
    try:
        delete_event("EID03")
        print("Event deleted successfully.")
    except Exception as e:
        print("Error in delete_event:", e)

def test_assign_student():
    print("\nTesting: assign_student")
    try:
        assign_student("EID02", "BSSTUDE06", "Stage Setup Manager")
        print("Student assigned successfully.")
    except Exception as e:
        print("Error in assign_student:", e)

def test_insert_event_file():
    print("\nTesting: insert_event_file")
    file_id = generate_unique_file_id()  # Generate the next FileID
    try:
        insert_event_file(file_id, "EID02", "BSSTUDE03", "Stage_Setup_Plan.pdf")
        print("Event file record inserted successfully.")
    except Exception as e:
        print("Error in insert_event_file:", e)

def test_insert_feedback():
    print("\nTesting: insert_feedback")
    feedback_id = generate_unique_feedback_id()  # Generate the next FeedbackID
    try:
        insert_feedback(feedback_id, "FILEID-003", "BSTEACH02", "Add more clarity to the rules section.")
        print("Feedback inserted successfully.")
    except Exception as e:
        print("Error in insert_feedback:", e)

def test_save_uploaded_file():
    print("\nTesting: save_uploaded_file")
    try:
        src_path = "C:/path/to/dummy_report.pdf"  # Change this to a valid file path
        dest_filename = "uploaded_report.pdf"
        dest_path = save_uploaded_file(src_path, dest_filename)
        print("File saved successfully at:", dest_path)
    except Exception as e:
        print("Error in save_uploaded_file:", e)

if __name__ == "__main__":
    test_get_user()
    test_insert_event()
    test_update_event()
    test_delete_event()
    test_assign_student()
    test_insert_event_file()
    test_insert_feedback()
    test_save_uploaded_file()
