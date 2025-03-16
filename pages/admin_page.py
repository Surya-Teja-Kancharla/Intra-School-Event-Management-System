from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox, Text, ttk
from tkcalendar import Calendar, DateEntry
import sys
import os
from database.db_connection import get_connection

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class AdminDashboard:
    def __init__(self, root, user_id):
        self.root = root
        self.user_id = user_id
        self.root.title("Admin Dashboard - Intra-School Event Management")
        self.root.configure(bg="#f0f0f0")
        self.root.geometry("700x500")

        # PostgreSQL connection
        try:
            self.conn = get_connection()
            self.cursor = self.conn.cursor()
        except Exception as e:
            messagebox.showerror("Database Connection Error", f"Error connecting to the database: {e}")
            self.conn = None
            self.cursor = None

        self.create_widgets()

    def create_widgets(self):
        header = tk.Label(self.root, text="Admin Dashboard", font=("Arial", 18, "bold"), bg="#f0f0f0")
        header.pack(pady=20)

        btn_frame = tk.Frame(self.root, bg="#f0f0f0")
        btn_frame.pack(pady=10)

        btn_style = {"font": ("Arial", 12), "width": 25, "bd": 2, "relief": "raised"}
        tk.Button(btn_frame, text="Dashboard", bg="#007BFF", fg="white", **btn_style, command=self.dashboard).grid(row=0, column=0, pady=10)
        tk.Button(btn_frame, text="Add Teachers", bg="#007BFF", fg="white", **btn_style, command=self.add_teachers).grid(row=1, column=0, pady=10)
        tk.Button(btn_frame, text="Add Events", bg="#007BFF", fg="white", **btn_style, command=self.add_events).grid(row=2, column=0, pady=10)
        tk.Button(btn_frame, text="Edit Events", bg="#007BFF", fg="white", **btn_style, command=self.edit_events).grid(row=3, column=0, pady=10)
        tk.Button(btn_frame, text="Delete Events", bg="#DC3545", fg="white", **btn_style, command=self.delete_events).grid(row=4, column=0, pady=10)
        tk.Button(btn_frame, text="Logout", bg="#DC3545", fg="white", **btn_style, command=self.logout).grid(row=5, column=0, pady=10)

    def dashboard(self):
        """Opens the Dashboard window with a calendar that highlights event dates based on the database."""
        dash_win = tk.Toplevel(self.root)
        dash_win.title("Dashboard")
        dash_win.geometry("600x500")
        dash_win.configure(bg="white")

        tk.Label(dash_win, text="Dashboard", font=("Arial", 16, "bold"), bg="white").pack(pady=10)

        cal_frame = tk.Frame(dash_win, bg="white")
        cal_frame.pack(pady=10)

        calendar = Calendar(cal_frame, selectmode='day', date_pattern="yyyy-mm-dd", font=("Arial", 12))
        calendar.pack(padx=20, pady=10)

        today = datetime.today().date()

        # Fetch events from the database
        try:
            query = "SELECT EventName, EventDate FROM Events"
            self.cursor.execute(query)
            events = self.cursor.fetchall()

            for event_name, event_date in events:
                # Ensure event_date is in date format
                if isinstance(event_date, str):
                    event_date = datetime.strptime(event_date, "%Y-%m-%d").date()

                if event_date < today:
                    tag = "completed"  # Completed event
                elif event_date > today:
                    tag = "upcoming"  # Upcoming event
                else:
                    tag = "current"  # Current event

                calendar.calevent_create(event_date, event_name, tag)

            # Configure tags with distinct colors
            calendar.tag_config("completed", background="red", foreground="white")
            calendar.tag_config("upcoming", background="green", foreground="white")
            calendar.tag_config("current", background="blue", foreground="white")

        except Exception as e:
            messagebox.showerror("Error", f"Error fetching events: {e}")
            return

        # Label for instructions
        instruction_label = tk.Label(dash_win, text="Event dates are highlighted on the calendar.", font=("Arial", 12), bg="white")
        instruction_label.pack(pady=10)

        # Textbox to display event details
        event_details = Text(dash_win, height=5, width=60, font=("Arial", 12), state="disabled")
        event_details.pack(pady=10)

        def on_date_select(event):
            """Handles the selection of a date on the calendar."""
            selected_date = calendar.get_date()
            try:
                query = "SELECT EventName FROM Events WHERE EventDate = %s"
                self.cursor.execute(query, (selected_date,))
                results = self.cursor.fetchall()

                event_details.config(state="normal")
                event_details.delete("1.0", tk.END)

                if results:
                    for row in results:
                        event_details.insert(tk.END, f"Event: {row[0]}\n")
                else:
                    event_details.insert(tk.END, "No events on the selected day.")

                event_details.config(state="disabled")

            except Exception as e:
                messagebox.showerror("Error", f"Error fetching events for the selected date: {e}")

        # Bind the calendar date selection event
        calendar.bind("<<CalendarSelected>>", on_date_select)

    def add_teachers(self):
        """Handles adding new teachers to the system."""
        def submit_teacher():
            user_id = user_id_entry.get().strip()
            first_name = fname_entry.get().strip()
            last_name = lname_entry.get().strip()

            if not user_id or not first_name or not last_name:
                messagebox.showerror("Error", "All fields are required!")
                return

            try:
                query_users = """
                    INSERT INTO Users (UserID, UserName, UserRole, UserPass)
                    VALUES (%s, %s, 'Teacher', %s)
                """
                user_pass = f"{first_name.lower()}@123"
                self.cursor.execute(query_users, (user_id, first_name, user_pass))

                query_teachers = """
                    INSERT INTO Teachers (UserID, TeacherFName, TeacherLName)
                    VALUES (%s, %s, %s)
                """
                self.cursor.execute(query_teachers, (user_id, first_name, last_name))
                self.conn.commit()

                messagebox.showinfo("Success", f"Teacher {first_name} added successfully!")
                add_window.destroy()
            except Exception as e:
                self.conn.rollback()
                messagebox.showerror("Database Error", f"Error adding teacher: {e}")

        add_window = tk.Toplevel(self.root)
        add_window.title("Add Teachers")
        add_window.geometry("400x300")
        add_window.configure(bg="white")

        tk.Label(add_window, text="Add Teacher", font=("Arial", 16, "bold"), bg="white").pack(pady=10)
        frame = tk.Frame(add_window, bg="white", padx=20, pady=20)
        frame.pack(pady=10)

        tk.Label(frame, text="Teacher ID:", font=("Arial", 12), bg="white").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        user_id_entry = tk.Entry(frame, font=("Arial", 12), width=20)
        user_id_entry.grid(row=0, column=1, pady=5)

        tk.Label(frame, text="First Name:", font=("Arial", 12), bg="white").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        fname_entry = tk.Entry(frame, font=("Arial", 12), width=20)
        fname_entry.grid(row=1, column=1, pady=5)

        tk.Label(frame, text="Last Name:", font=("Arial", 12), bg="white").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        lname_entry = tk.Entry(frame, font=("Arial", 12), width=20)
        lname_entry.grid(row=2, column=1, pady=5)

        tk.Button(add_window, text="Submit", font=("Arial", 12, "bold"), bg="#007BFF", fg="white", width=15, command=submit_teacher).pack(pady=10)

    def add_events(self):
        """Admin functionality to add events."""
        def submit_event():
            event_name = event_name_entry.get().strip()
            event_date = event_date_entry.get().strip()
            start_time = start_time_entry.get().strip()
            end_time = end_time_entry.get().strip()
            venue = venue_var.get().strip()
            selected_teacher = teacher_var.get()

            if not event_name or not event_date or not start_time or not end_time or venue == "Select Venue" or selected_teacher == "Select Teacher":
                messagebox.showerror("Error", "All fields are required!")
                return

            try:
                # Format event_date
                day, month, year = map(int, event_date.split('/'))
                formatted_date = f"{year:04d}-{month:02d}-{day:02d}"

                # Validate times
                if start_time >= end_time:
                    messagebox.showerror("Error", "Start time must be before end time!")
                    return

                # Generate EventID
                query_id = "SELECT MAX(EventID) FROM Events"
                self.cursor.execute(query_id)
                max_id = self.cursor.fetchone()[0]
                if max_id:
                    numeric_part = int(max_id[3:])  # Extract numeric part
                    event_id = f"EID{numeric_part + 1:02d}"  # Increment and format
                else:
                    event_id = "EID001"  # Default ID

                user_id = selected_teacher.split(" - ")[0]  # Extract TeacherID which is UserID

                # Insert event into the database
                query = """
                    INSERT INTO Events (EventID, EventName, EventDate, EventStartTime, EventEndTime, EventVenue, UserID)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                values = (event_id, event_name, formatted_date, start_time, end_time, venue, user_id)
                self.cursor.execute(query, values)
                self.conn.commit()

                messagebox.showinfo("Success", f"Event '{event_name}' created successfully!")
                add_event_win.destroy()
            except Exception as e:
                self.conn.rollback()
                messagebox.showerror("Database Error", f"Error adding event: {e}")

        def fetch_available_teachers(event_date):
            """Fetch teachers who are not assigned to events within 3 days of the given date."""
            try:
                query = """
                    SELECT Teachers.UserID, Users.UserName
                    FROM Teachers
                    JOIN Users ON Teachers.UserID = Users.UserID
                    WHERE Teachers.UserID NOT IN (
                        SELECT e.UserID
                        FROM Events e
                        WHERE e.EventDate BETWEEN (%s::DATE - INTERVAL '3 days') AND (%s::DATE + INTERVAL '3 days')
                    )
                """
                self.cursor.execute(query, (event_date, event_date))
                return [f"{row[0]} - {row[1]}" for row in self.cursor.fetchall()]
            except Exception as e:
                messagebox.showerror("Error", f"Error fetching teachers: {e}")
                return []


        add_event_win = tk.Toplevel(self.root)
        add_event_win.title("Add Event")
        add_event_win.geometry("500x500")
        add_event_win.configure(bg="white")

        tk.Label(add_event_win, text="Add Event", font=("Arial", 16, "bold"), bg="white").pack(pady=10)

        frame = tk.Frame(add_event_win, bg="white", padx=20, pady=20)
        frame.pack(pady=10)

        # Event Name
        tk.Label(frame, text="Event Name:", font=("Arial", 12), bg="white").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        event_name_entry = tk.Entry(frame, font=("Arial", 12), width=25)
        event_name_entry.grid(row=0, column=1, pady=5)

        # Event Date
        tk.Label(frame, text="Event Date (DD/MM/YYYY):", font=("Arial", 12), bg="white").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        event_date_entry = DateEntry(frame, font=("Arial", 12), width=22, date_pattern="dd/MM/yyyy")
        event_date_entry.grid(row=1, column=1, pady=5)

        # Start Time
        tk.Label(frame, text="Start Time:", font=("Arial", 12), bg="white").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        start_time_entry = tk.Entry(frame, font=("Arial", 12), width=25)
        start_time_entry.grid(row=2, column=1, pady=5)

        # End Time
        tk.Label(frame, text="End Time:", font=("Arial", 12), bg="white").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        end_time_entry = tk.Entry(frame, font=("Arial", 12), width=25)
        end_time_entry.grid(row=3, column=1, pady=5)

        # Venue
        tk.Label(frame, text="Venue:", font=("Arial", 12), bg="white").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        venue_var = tk.StringVar(value="Select Venue")
        venues = ["Central Auditorium", "Sports Ground", "Classroom"]
        venue_menu = tk.OptionMenu(frame, venue_var, *venues)
        venue_menu.config(font=("Arial", 12), width=20)
        venue_menu.grid(row=4, column=1, pady=5)

        # Teacher Dropdown
        tk.Label(frame, text="Assign Teacher:", font=("Arial", 12), bg="white").grid(row=5, column=0, sticky="e", padx=5, pady=5)
        teacher_var = tk.StringVar(value="Select Teacher")
        teacher_menu = tk.OptionMenu(frame, teacher_var, "Select Event Date First")
        teacher_menu.config(font=("Arial", 12), width=20)
        teacher_menu.grid(row=5, column=1, pady=5)

        def update_teacher_dropdown(*args):
            selected_date = event_date_entry.get_date()
            formatted_date = selected_date.strftime("%Y-%m-%d")
            teachers = fetch_available_teachers(formatted_date)
            teacher_menu["menu"].delete(0, "end")
            for teacher in teachers:
                teacher_menu["menu"].add_command(label=teacher, command=tk._setit(teacher_var, teacher))

        event_date_entry.bind("<<DateEntrySelected>>", update_teacher_dropdown)

        # Submit Button
        tk.Button(add_event_win, text="Submit Event", font=("Arial", 12, "bold"), bg="#007BFF", fg="white", width=15, command=submit_event).pack(pady=10)


    def edit_events(self):
        """Admin functionality to edit events."""
        def fetch_events():
            """Fetch all events for the dropdown."""
            try:
                self.cursor.execute("SELECT EventID, EventName, EventDate FROM Events")
                return [f"{row[0]} - {row[1]} ({row[2]})" for row in self.cursor.fetchall()]
            except Exception as e:
                messagebox.showerror("Error", f"Error fetching events: {e}")
                return []

        def fetch_event_details(event_id):
            """Fetch details of a specific event."""
            try:
                query = """
                    SELECT EventName, EventDate, EventStartTime, EventEndTime, EventVenue
                    FROM Events
                    WHERE EventID = %s
                """
                self.cursor.execute(query, (event_id,))
                return self.cursor.fetchone()
            except Exception as e:
                messagebox.showerror("Error", f"Error fetching event details: {e}")
                return None

        def fetch_teacher_conflicts(new_date, exclude_event):
            """Fetch teachers unavailable for the given date."""
            try:
                query = """
                    SELECT DISTINCT e.UserID
                    FROM Events e
                    WHERE e.EventID != %s 
                    AND %s BETWEEN (e.EventDate - INTERVAL '3 days') AND (e.EventDate + INTERVAL '3 days')
                """
                self.cursor.execute(query, (exclude_event, new_date))
                return [row[0] for row in self.cursor.fetchall()]
            except Exception as e:
                messagebox.showerror("Error", f"Error fetching conflicts: {e}")
                return []

        def populate_event_data(*args):
            """Populate event details when an event is selected."""
            selected_event = event_var.get()
            if selected_event == "Select Event":
                return
            
            event_id = selected_event.split(" - ")[0]
            event_details = fetch_event_details(event_id)

            if event_details:
                event_name, event_date, start_time, end_time, venue = event_details
                event_name_entry.delete(0, tk.END)
                event_name_entry.insert(0, event_name)
                event_date_entry.set_date(event_date)
                start_time_entry.delete(0, tk.END)
                start_time_entry.insert(0, start_time)
                end_time_entry.delete(0, tk.END)
                end_time_entry.insert(0, end_time)
                venue_var.set(venue)

        def submit_changes():
            selected_event = event_var.get()
            new_name = event_name_entry.get().strip()
            new_date = event_date_entry.get_date().strftime("%Y-%m-%d")
            new_start_time = start_time_entry.get().strip()
            new_end_time = end_time_entry.get().strip()
            new_venue = venue_var.get()

            if not selected_event or not new_name or not new_date or not new_start_time or not new_end_time or new_venue == "Select Venue":
                messagebox.showerror("Error", "All fields are required!")
                return

            event_id = selected_event.split(" - ")[0]

            # Validate dates and conflicts
            conflicting_teachers = fetch_teacher_conflicts(new_date, event_id)
            if conflicting_teachers:
                messagebox.showerror("Error", "The selected teacher is unavailable on the new date!")
                return

            try:
                query = """
                    UPDATE Events
                    SET EventName = %s, EventDate = %s, EventStartTime = %s, EventEndTime = %s, EventVenue = %s
                    WHERE EventID = %s
                """
                self.cursor.execute(query, (new_name, new_date, new_start_time, new_end_time, new_venue, event_id))
                self.conn.commit()
                messagebox.showinfo("Success", "Event updated successfully!")
                edit_win.destroy()
            except Exception as e:
                self.conn.rollback()
                messagebox.showerror("Database Error", f"Error updating event: {e}")

        edit_win = tk.Toplevel(self.root)
        edit_win.title("Edit Events")
        edit_win.geometry("600x500")
        edit_win.configure(bg="white")

        tk.Label(edit_win, text="Edit Event", font=("Arial", 16, "bold"), bg="white").pack(pady=10)

        # Events Dropdown
        tk.Label(edit_win, text="Select Event:", font=("Arial", 12), bg="white").pack(anchor="w", padx=20)
        event_var = tk.StringVar(value="Select Event")
        event_menu = ttk.Combobox(edit_win, textvariable=event_var, values=fetch_events(), state="readonly", font=("Arial", 12))
        event_menu.pack(pady=10)
        event_menu.bind("<<ComboboxSelected>>", populate_event_data)

        frame = tk.Frame(edit_win, bg="white", padx=20, pady=20)
        frame.pack(pady=10)

        # Event Details
        tk.Label(frame, text="Event Name:", font=("Arial", 12), bg="white").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        event_name_entry = tk.Entry(frame, font=("Arial", 12), width=30)
        event_name_entry.grid(row=0, column=1, pady=5)

        tk.Label(frame, text="Event Date (YYYY-MM-DD):", font=("Arial", 12), bg="white").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        event_date_entry = DateEntry(frame, font=("Arial", 12), width=28, date_pattern="yyyy-MM-dd")
        event_date_entry.grid(row=1, column=1, pady=5)

        tk.Label(frame, text="Start Time:", font=("Arial", 12), bg="white").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        start_time_entry = tk.Entry(frame, font=("Arial", 12), width=30)
        start_time_entry.grid(row=2, column=1, pady=5)

        tk.Label(frame, text="End Time:", font=("Arial", 12), bg="white").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        end_time_entry = tk.Entry(frame, font=("Arial", 12), width=30)
        end_time_entry.grid(row=3, column=1, pady=5)

        tk.Label(frame, text="Venue:", font=("Arial", 12), bg="white").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        venue_var = tk.StringVar(value="Select Venue")
        venues = ["Central Auditorium", "Sports Ground", "Classroom"]
        venue_menu = tk.OptionMenu(frame, venue_var, *venues)
        venue_menu.config(font=("Arial", 12), width=20)
        venue_menu.grid(row=4, column=1, pady=5)

        tk.Button(edit_win, text="Submit Changes", font=("Arial", 12, "bold"), bg="#007BFF", fg="white", width=20, command=submit_changes).pack(pady=20)


    def delete_events(self):
        """Admin functionality to delete events."""
        def delete_event():
            selected_event = event_var.get()
            if selected_event == "Select Event":
                messagebox.showerror("Error", "Please select a valid event to delete!")
                return

            event_id = selected_event.split(" - ")[0]
            try:
                # Delete from dependent tables
                query_delete_participation = "DELETE FROM Event_Participation WHERE EventID = %s"
                self.cursor.execute(query_delete_participation, (event_id,))

                # Delete from Events table
                query_delete_event = "DELETE FROM Events WHERE EventID = %s"
                self.cursor.execute(query_delete_event, (event_id,))
                self.conn.commit()

                messagebox.showinfo("Success", f"Event {selected_event} deleted successfully!")
                delete_window.destroy()
            except Exception as e:
                self.conn.rollback()
                messagebox.showerror("Database Error", f"Error deleting event: {e}")

        # UI for deleting an event
        delete_window = tk.Toplevel(self.root)
        delete_window.title("Delete Events")
        delete_window.geometry("400x300")
        delete_window.configure(bg="white")

        tk.Label(delete_window, text="Delete Event", font=("Arial", 16, "bold"), bg="white").pack(pady=10)

        frame = tk.Frame(delete_window, bg="white", padx=20, pady=20)
        frame.pack(pady=10)

        tk.Label(frame, text="Select Event:", font=("Arial", 12), bg="white").grid(row=0, column=0, sticky="e", padx=5, pady=5)

        event_var = tk.StringVar(value="Select Event")
        event_menu = tk.OptionMenu(frame, event_var, "Loading...")
        event_menu.config(font=("Arial", 12), width=30)
        event_menu.grid(row=0, column=1, pady=5)

        # Populate events dropdown
        try:
            query = "SELECT EventID, EventName FROM Events"
            self.cursor.execute(query)
            events = self.cursor.fetchall()

            if events:
                event_menu["menu"].delete(0, "end")
                for event in events:
                    event_menu["menu"].add_command(label=f"{event[0]} - {event[1]}", command=tk._setit(event_var, f"{event[0]} - {event[1]}"))
            else:
                event_menu["menu"].delete(0, "end")
                event_menu["menu"].add_command(label="No Events Available", command=lambda: None)

        except Exception as e:
            messagebox.showerror("Database Error", f"Error fetching events: {e}")

        tk.Button(
            delete_window, text="Delete Event", font=("Arial", 12, "bold"), bg="#DC3545", fg="white", width=15, command=delete_event
        ).pack(pady=10)

    def logout(self):
        self.root.destroy()
        from pages.login_page import LoginPage
        root = tk.Tk()
        LoginPage(root)
        root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    AdminDashboard(root)
    root.mainloop()
