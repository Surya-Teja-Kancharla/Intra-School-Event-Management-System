from datetime import timedelta
import tkinter as tk
from tkinter import messagebox, ttk
import sys
import os
from database.db_connection import get_connection

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Make sure tkcalendar is installed if you're using it for "Create Events"
try:
    from tkcalendar import DateEntry
    CALENDAR_AVAILABLE = True
except ImportError:
    CALENDAR_AVAILABLE = False

class TeacherDashboard:
    def __init__(self, root, user_id):
        self.root = root
        self.user_id = user_id
        self.root.title("Teacher Dashboard - Intra-School Event Management")
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
        """
        Main Teacher Dashboard with exactly four buttons:
        1. Create Events
        2. Add Students
        3. Provide Feedback
        4. Logout
        """
        header = tk.Label(self.root, text="Teacher Dashboard", font=("Arial", 18, "bold"), bg="#f0f0f0")
        header.pack(pady=20)

        btn_frame = tk.Frame(self.root, bg="#f0f0f0")
        btn_frame.pack(pady=10)

        btn_style = {"font": ("Arial", 12), "width": 25, "bd": 2, "relief": "raised"}

        # Button 1: Create Events
        tk.Button(
            btn_frame,
            text="Create Events",
            bg="#007BFF",
            fg="white",
            **btn_style,
            command=self.create_events
        ).grid(row=0, column=0, pady=10)

        # Button 2: Add Students
        tk.Button(
            btn_frame,
            text="Add Students",
            bg="#007BFF",
            fg="white",
            **btn_style,
            command=self.add_students
        ).grid(row=1, column=0, pady=10)

        # Button 3: Provide Feedback
        tk.Button(
            btn_frame,
            text="Provide Feedback",
            bg="#007BFF",
            fg="white",
            **btn_style,
            command=self.provide_feedback
        ).grid(row=2, column=0, pady=10)

        # Button 4: Logout
        tk.Button(
            btn_frame,
            text="Logout",
            bg="#DC3545",
            fg="white",
            **btn_style,
            command=self.logout
        ).grid(row=3, column=0, pady=10)

    # ----------------------------------------------------
    # 1. Create Events
    # ----------------------------------------------------
    def create_events(self):
        """
        Opens a window to create new events.
        Includes fields for Event Name, Date, Start/End Time, Venue.
        """
        def save_event():
            # Retrieve input data
            event_name = event_name_entry.get().strip()
            event_date = event_date_entry.get().strip()
            start_time = start_time_entry.get().strip()
            end_time = end_time_entry.get().strip()
            venue = venue_var.get().strip()

            # Validate inputs
            if not event_name or not event_date or not start_time or not end_time or venue == "Select Venue":
                messagebox.showerror("Error", "All fields are required!")
                return

            try:
                # Convert event_date from DD/MM/YYYY to YYYY-MM-DD
                day, month, year = map(int, event_date.split('/'))
                formatted_date = f"{year:04d}-{month:02d}-{day:02d}"

                # Example validation: Start time should be before End time
                if start_time >= end_time:
                    messagebox.showerror("Error", "Start time must be before End time.")
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

                # Assuming 'UserID' of the logged-in teacher is available as 'self.user_id'
                user_id = self.user_id  # Replace this with the actual logged-in user's ID

                # Save to database
                query = """
                    INSERT INTO Events (EventID, EventName, EventDate, EventStartTime, EventEndTime, EventVenue, UserID)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                values = (event_id, event_name, formatted_date, start_time, end_time, venue, user_id)
                self.cursor.execute(query, values)
                self.conn.commit()

                # Success message
                messagebox.showinfo("Success", f"Event '{event_name}' created successfully!")
                create_win.destroy()
            except ValueError:
                messagebox.showerror("Error", "Invalid date format! Please use DD/MM/YYYY.")
            except Exception as e:
                messagebox.showerror("Database Error", f"An error occurred: {e}")


        # Create Event Window
        create_win = tk.Toplevel(self.root)
        create_win.title("Create Event")
        create_win.geometry("500x400")
        create_win.configure(bg="white")

        tk.Label(create_win, text="Create Event", font=("Arial", 16, "bold"), bg="white").pack(pady=10)

        frame = tk.Frame(create_win, bg="white", padx=20, pady=20)
        frame.pack(pady=10)

        # Event Name
        tk.Label(frame, text="Event Name:", font=("Arial", 12), bg="white").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        event_name_entry = tk.Entry(frame, font=("Arial", 12), width=25)
        event_name_entry.grid(row=0, column=1, pady=5)

        # Event Date
        tk.Label(frame, text="Event Date (DD/MM/YYYY):", font=("Arial", 12), bg="white").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        if CALENDAR_AVAILABLE:
            event_date_entry = DateEntry(frame, font=("Arial", 12), width=22, date_pattern="dd/MM/yyyy")
            event_date_entry.grid(row=1, column=1, pady=5)
        else:
            event_date_entry = tk.Entry(frame, font=("Arial", 12), width=25)
            event_date_entry.insert(0, "DD/MM/YYYY")
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

        # Submit Button
        tk.Button(
            create_win,
            text="Create Event",
            font=("Arial", 12, "bold"),
            bg="#007BFF",
            fg="white",
            width=15,
            command=save_event
        ).pack(pady=10)


    # ----------------------------------------------------
    # 2. Add Students
    # ----------------------------------------------------
    def add_students(self):
        """
        Opens a window to add students to an event or assign roles.
        Dynamically fetches events and students based on the teacher's user_id.
        """
        def fetch_teacher_events():
            """
            Fetches events associated with the logged-in teacher.
            """
            try:
                query = "SELECT EventID, EventName FROM Events WHERE UserID = %s"
                self.cursor.execute(query, (self.user_id,))
                result = self.cursor.fetchall()
                return [(row[0], row[1]) for row in result]  # Return a list of (EventID, EventName)
            except Exception as e:
                messagebox.showerror("Database Error", f"Error fetching events: {e}")
                return []

        def fetch_available_students(selected_event_id):
            """
            Fetches students not assigned to events and those who meet the criteria for the selected event.
            """
            try:
                # Get the event date for the selected event
                query_event_date = "SELECT EventDate FROM Events WHERE EventID = %s"
                self.cursor.execute(query_event_date, (selected_event_id,))
                event_date = self.cursor.fetchone()[0]

                # Fetch students who are not assigned to any event
                query_no_event = """
                    SELECT Students.UserID, Users.UserName 
                    FROM Students
                    JOIN Users ON Students.UserID = Users.UserID
                    WHERE Students.UserID NOT IN (SELECT UserID FROM Event_Participation)
                """

                query_not_conflicting = """
                    SELECT Students.UserID, Users.UserName 
                    FROM Students
                    JOIN Users ON Students.UserID = Users.UserID
                    WHERE Students.UserID NOT IN (
                        SELECT ep.UserID
                        FROM Event_Participation ep
                        JOIN Events e ON ep.EventID = e.EventID
                        WHERE e.EventDate BETWEEN %s AND %s
                    )
                """


                # Calculate date range (3 days before and 3 days after the event date)
                date_start = (event_date - timedelta(days=3)).strftime('%Y-%m-%d')
                date_end = (event_date + timedelta(days=3)).strftime('%Y-%m-%d')

                # Execute queries
                self.cursor.execute(query_no_event)
                no_event_students = self.cursor.fetchall()

                self.cursor.execute(query_not_conflicting, (date_start, date_end))
                not_conflicting_students = self.cursor.fetchall()

                # Merge results and ensure unique entries
                unique_students = {row[0]: row[1] for row in no_event_students + not_conflicting_students}

                # Return formatted list of (StudentID, StudentName)
                return [(student_id, student_name) for student_id, student_name in unique_students.items()]
            except Exception as e:
                messagebox.showerror("Database Error", f"Error fetching students: {e}")
                return []

        def add_student_to_event():
            """
            Adds the selected student to the selected event with the specified responsibility.
            """
            selected_event = event_var.get()
            selected_student = student_var.get()
            responsibility = responsibility_entry.get().strip()

            if selected_event == "Select Event" or selected_student == "Select Student" or not responsibility:
                messagebox.showerror("Error", "All fields are required!")
                return

            try:
                event_id = selected_event.split(" - ")[0]
                student_id = selected_student.split(" - ")[0]

                query_insert = """
                    INSERT INTO Event_Participation (EventID, UserID, Responsibility)
                    VALUES (%s, %s, %s)
                """
                self.cursor.execute(query_insert, (event_id, student_id, responsibility))
                self.conn.commit()

                messagebox.showinfo("Success", f"Student {selected_student} assigned to event successfully!")
                add_win.destroy()
            except Exception as e:
                messagebox.showerror("Database Error", f"Error assigning student to event: {e}")

        add_win = tk.Toplevel(self.root)
        add_win.title("Add Students")
        add_win.geometry("600x500")
        add_win.configure(bg="white")

        tk.Label(add_win, text="Add Students", font=("Arial", 16, "bold"), bg="white").pack(pady=10)

        frame = tk.Frame(add_win, bg="white", padx=20, pady=20)
        frame.pack(pady=10)

        # Fetch events associated with the teacher
        teacher_events = fetch_teacher_events()
        if not teacher_events:
            messagebox.showerror("Error", "No events found for this teacher!")
            add_win.destroy()
            return

        # Event Dropdown
        tk.Label(frame, text="Select Event:", font=("Arial", 12), bg="white").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        event_var = tk.StringVar(value="Select Event")
        event_menu = tk.OptionMenu(frame, event_var, *[f"{eid} - {ename}" for eid, ename in teacher_events])
        event_menu.config(font=("Arial", 12), width=30)
        event_menu.grid(row=0, column=1, pady=5)

        # Fetch students dynamically when an event is selected
        def on_event_select(*args):
            selected_event_id = event_var.get().split(" - ")[0]
            available_students = fetch_available_students(selected_event_id)

            # Update the students dropdown
            student_menu["menu"].delete(0, "end")
            for sid, sname in available_students:
                student_menu["menu"].add_command(label=f"{sid} - {sname}", command=tk._setit(student_var, f"{sid} - {sname}"))

            student_var.set("Select Student")

        event_var.trace("w", on_event_select)

        # Student Dropdown
        tk.Label(frame, text="Select Student:", font=("Arial", 12), bg="white").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        student_var = tk.StringVar(value="Select Student")
        student_menu = tk.OptionMenu(frame, student_var, "Select Event First")
        student_menu.config(font=("Arial", 12), width=30)
        student_menu.grid(row=1, column=1, pady=5)

        # Responsibility / Role
        tk.Label(frame, text="Responsibility:", font=("Arial", 12), bg="white").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        responsibility_entry = tk.Entry(frame, font=("Arial", 12), width=30)
        responsibility_entry.grid(row=2, column=1, pady=5)

        # Submit Button
        tk.Button(
            add_win,
            text="Add",
            font=("Arial", 12, "bold"),
            bg="#007BFF",
            fg="white",
            width=15,
            command=add_student_to_event
        ).pack(pady=10)



    # ----------------------------------------------------
    # 3. Provide Feedback
    # ----------------------------------------------------
    def provide_feedback(self):
        """
        Opens a window for the teacher to:
        (a) Select a student ID to view that student’s files.
        (b) Display file format and size.
        (c) Large text box to add feedback.
        (d) Approve or Decline buttons (no separate Submit).
        """
        feedback_win = tk.Toplevel(self.root)
        feedback_win.title("Provide Feedback")
        feedback_win.geometry("600x500")
        feedback_win.configure(bg="white")

        # -- Top Section: Select Student Uploads --
        top_label = tk.Label(feedback_win, text="Select Student Uploads", font=("Arial", 14, "bold"), bg="white")
        top_label.pack(pady=10)

        top_frame = tk.Frame(feedback_win, bg="white", padx=20, pady=10)
        top_frame.pack()

        # Student ID
        tk.Label(top_frame, text="Student ID:", font=("Arial", 12), bg="white").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.student_var = tk.StringVar(value="Select Student")
        student_ids = ["S001", "S002", "S003"]  # Dummy data
        student_id_menu = ttk.Combobox(top_frame, textvariable=self.student_var, values=student_ids, state="readonly", width=18)
        student_id_menu.grid(row=0, column=1, padx=5, pady=5)

        # Load Files Button
        tk.Button(
            top_frame,
            text="Load Files",
            font=("Arial", 12, "bold"),
            bg="#007BFF",
            fg="white",
            command=self.load_files
        ).grid(row=0, column=2, padx=10, pady=5)

        # Treeview to display File Name, Format, and Size
        self.files_tree = ttk.Treeview(feedback_win, columns=("FileName", "Format", "Size"), show="headings", height=5)
        self.files_tree.heading("FileName", text="File Name")
        self.files_tree.heading("Format", text="Format")
        self.files_tree.heading("Size", text="Size (KB)")

        self.files_tree.column("FileName", width=200)
        self.files_tree.column("Format", width=80)
        self.files_tree.column("Size", width=80)

        self.files_tree.pack(padx=20, pady=10)

        # -- Bottom Section: Enter Feedback --
        bottom_label = tk.Label(feedback_win, text="Enter Feedback", font=("Arial", 14, "bold"), bg="white")
        bottom_label.pack(pady=10)

        feedback_frame = tk.Frame(feedback_win, bg="white", padx=20, pady=10)
        feedback_frame.pack()

        self.feedback_text = tk.Text(feedback_frame, font=("Arial", 12), width=60, height=6, bd=2, relief="sunken")
        self.feedback_text.pack(pady=5)

        # Approve / Decline Buttons
        btn_frame = tk.Frame(feedback_win, bg="white")
        btn_frame.pack(pady=10)

        tk.Button(
            btn_frame,
            text="Approve",
            font=("Arial", 12, "bold"),
            bg="#28A745",
            fg="white",
            width=10,
            command=lambda: messagebox.showinfo("Feedback", "Submission approved (dummy)")
        ).grid(row=0, column=0, padx=10)

        tk.Button(
            btn_frame,
            text="Decline",
            font=("Arial", 12, "bold"),
            bg="#DC3545",
            fg="white",
            width=10,
            command=lambda: messagebox.showinfo("Feedback", "Submission declined (dummy)")
        ).grid(row=0, column=1, padx=10)

    def load_files(self):
        """
        Dummy function to load a student's files and display them in the Treeview.
        Real implementation would fetch data from DB or filesystem.
        """
        # Clear the treeview first
        for item in self.files_tree.get_children():
            self.files_tree.delete(item)

        # Example dummy data
        # (FileName, Format, Size)
        dummy_data = [
            ("ProjectReport.docx", "DOCX", "240"),
            ("Presentation.pdf", "PDF", "1200"),
            ("Diagram.png", "PNG", "560"),
        ]

        for file_info in dummy_data:
            self.files_tree.insert("", tk.END, values=file_info)

        messagebox.showinfo("Load Files", f"Files for student {self.student_var.get()} loaded (dummy).")

    # ----------------------------------------------------
    # 4. Logout
    # ----------------------------------------------------
    def logout(self):
        self.root.destroy()
        from pages.login_page import LoginPage
        root = tk.Tk()
        LoginPage(root)
        root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    TeacherDashboard(root)
    root.mainloop()
