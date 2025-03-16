import os
from database.db_connection import get_connection
from dotenv import load_dotenv

# Load environment variables from .env file (if not already loaded in db_connection.py)
load_dotenv()

# -----------------------------------------------------------
# Helper Function: Generate Unique File Name for Uploads
# -----------------------------------------------------------
def generate_upload_filename(user_id, event_id, original_filename):
    """
    Generates a unique file name using user ID, event ID, and the original file name.
    Format: <userID>_<eventID>_<original_filename>
    """
    base_filename = os.path.basename(original_filename)
    new_filename = f"{user_id}_{event_id}_{base_filename}"
    return new_filename

# -----------------------------------------------------------
# 1. Fetching a User for Login
# -----------------------------------------------------------
def get_user(username, password, role):
    """
    Fetches a user record based on username, password, and role.
    Returns: (UserID, UserRole) tuple or None if not found.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = """
            SELECT UserID, UserRole FROM Users
            WHERE UserName = %s AND UserPass = %s AND UserRole = %s
        """
        cursor.execute(query, (username, password, role))
        result = cursor.fetchone()
        return result
    except Exception as e:
        print("Error fetching user:", e)
        raise e
    finally:
        cursor.close()
        conn.close()

# -----------------------------------------------------------
# 2. Inserting a New Event with Teacher Assignment
# -----------------------------------------------------------
def add_event_with_teacher(event_name, event_date, start_time, end_time, venue, teacher_id):
    """
    Inserts a new event into the Events table and assigns it to a teacher.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        event_id = generate_next_event_id()

        # Insert event into Events table
        query = """
            INSERT INTO Events (EventID, EventName, EventDate, EventStartTime, EventEndTime, EventVenue, UserID)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (event_id, event_name, event_date, start_time, end_time, venue, teacher_id))
        conn.commit()
        print(f"Event added successfully with ID: {event_id}")
        return event_id
    except Exception as e:
        conn.rollback()
        print("Error adding event:", e)
        raise e
    finally:
        cursor.close()
        conn.close()

# -----------------------------------------------------------
# 3. Fetch Available Teachers for a Given Event Date
# -----------------------------------------------------------
def fetch_available_teachers_for_date(event_date):
    """
    Fetches teachers who are not assigned to events within 3 days of the given event date.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = """
            SELECT Teachers.TeacherID, Users.UserName
            FROM Teachers
            JOIN Users ON Teachers.TeacherID = Users.UserID
            WHERE Teachers.TeacherID NOT IN (
                SELECT e.UserID
                FROM Events e
                WHERE ABS(DATE_PART('day', e.EventDate::date - %s::date)) <= 3
            )
        """
        cursor.execute(query, (event_date,))
        return [f"{row[0]} - {row[1]}" for row in cursor.fetchall()]
    except Exception as e:
        print("Error fetching available teachers:", e)
        raise e
    finally:
        cursor.close()
        conn.close()

# -----------------------------------------------------------
# 4. Updating an Existing Event
# -----------------------------------------------------------
def edit_event(event_id, new_name, new_date, new_start_time, new_end_time, new_venue):
    """
    Updates the details of an existing event, ensuring no conflicts with other events.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()

        # Check for conflicts with the teacher's assigned events
        query_conflicts = """
            SELECT UserID
            FROM Events
            WHERE ABS(DATE_PART('day', EventDate::date - %s::date)) <= 3
              AND EventID != %s
        """
        cursor.execute(query_conflicts, (new_date, event_id))
        conflicting_users = cursor.fetchall()

        if conflicting_users:
            raise ValueError("Conflict detected with other events for the assigned teacher!")

        # Update event in Events table
        query_update = """
            UPDATE Events
            SET EventName = %s,
                EventDate = %s,
                EventStartTime = %s,
                EventEndTime = %s,
                EventVenue = %s
            WHERE EventID = %s
        """
        cursor.execute(query_update, (new_name, new_date, new_start_time, new_end_time, new_venue, event_id))
        conn.commit()
        print(f"Event {event_id} updated successfully.")
    except Exception as e:
        conn.rollback()
        print("Error editing event:", e)
        raise e
    finally:
        cursor.close()
        conn.close()

# -----------------------------------------------------------
# 5. Deleting an Event with Integrity
# -----------------------------------------------------------
def delete_event_with_integrity(event_id):
    """
    Deletes an event after removing associated records in related tables.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()

        # Delete records from Event_Participation table
        query_delete_participation = "DELETE FROM Event_Participation WHERE EventID = %s"
        cursor.execute(query_delete_participation, (event_id,))

        # Delete records from Event_Files table
        query_delete_files = "DELETE FROM Event_Files WHERE EventID = %s"
        cursor.execute(query_delete_files, (event_id,))

        # Delete the event itself
        query_delete_event = "DELETE FROM Events WHERE EventID = %s"
        cursor.execute(query_delete_event, (event_id,))

        conn.commit()
        print(f"Event {event_id} and associated records deleted successfully.")
    except Exception as e:
        conn.rollback()
        print("Error deleting event:", e)
        raise e
    finally:
        cursor.close()
        conn.close()

# -----------------------------------------------------------
# 6. Generate Next Event ID
# -----------------------------------------------------------
def generate_next_event_id():
    """
    Generates the next EventID in the format 'EIDxx', where xx is incremented.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = "SELECT MAX(EventID) FROM Events"
        cursor.execute(query)
        max_id = cursor.fetchone()[0]
        if max_id:
            numeric_part = int(max_id[3:])
            next_id = f"EID{numeric_part + 1:02d}"
        else:
            next_id = "EID01"
        return next_id
    except Exception as e:
        print("Error generating next EventID:", e)
        raise e
    finally:
        cursor.close()
        conn.close()


# -----------------------------------------------------------
# 8. Fetch All Events
# -----------------------------------------------------------
def generate_unique_file_id():
    """
    Generates the next FileID in the format 'FILEID-00x',
    where x represents the next number after the current maximum.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = "SELECT MAX(FileID) FROM Event_Files"
        cursor.execute(query)
        max_id = cursor.fetchone()[0]
        if max_id:
            # Remove the 'FILEID-' prefix and convert the remaining part to an integer
            numeric_part = int(max_id.replace("FILEID-", ""))
            next_id = f"FILEID-{numeric_part + 1:03d}"
        else:
            next_id = "FILEID-001"
        return next_id
    except Exception as e:
        print("Error generating unique FileID:", e)
        raise e
    finally:
        cursor.close()
        conn.close()

# -----------------------------------------------------------
# 9. Fetch All Events
# -----------------------------------------------------------
def generate_unique_feedback():
    """
    Generates the next FeedbackID in the format 'FEEDBACK0x',
    where x is the next number after the current maximum.
    For example, if the maximum FeedbackID is "FEEDBACK01", the next will be "FEEDBACK02".
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = "SELECT MAX(FeedbackID) FROM Feedback"
        cursor.execute(query)
        max_id = cursor.fetchone()[0]
        if max_id:
            # Remove the 'FEEDBACK' prefix and convert the remaining part to an integer
            numeric_part = int(max_id.replace("FEEDBACK", ""))
            next_id = f"FEEDBACK{numeric_part + 1:02d}"
        else:
            next_id = "FEEDBACK01"
        return next_id
    except Exception as e:
        print("Error generating unique FeedbackID:", e)
        raise e
    finally:
        cursor.close()
        conn.close()


# -----------------------------------------------------------
# 10. Fetch All Events
# -----------------------------------------------------------
def fetch_all_events():
    """
    Fetches all events from the database.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = "SELECT EventID, EventName, EventDate FROM Events"
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print("Error fetching events:", e)
        raise e
    finally:
        cursor.close()
        conn.close()
