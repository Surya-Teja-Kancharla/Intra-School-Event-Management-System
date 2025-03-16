import os
import sys
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import timedelta
from database.db_connection import get_connection
from database.queries import generate_unique_feedback


# Append the parent directory (project root) to the Python path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

try:
    from tkcalendar import DateEntry
    CALENDAR_AVAILABLE = True
except ImportError:
    CALENDAR_AVAILABLE = False


# Helper function to underline text
def underline_text(text):
    return "".join([char + "\u0332" for char in text])

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
        header = tk.Label(self.root, text="Teacher Dashboard", font=("Arial", 18, "bold"), bg="#f0f0f0")
        header.pack(pady=20)

        btn_frame = tk.Frame(self.root, bg="#f0f0f0")
        btn_frame.pack(pady=10)

        btn_style = {"font": ("Arial", 12), "width": 25, "bd": 2, "relief": "raised"}

        tk.Button(btn_frame, text="Create Events", bg="#007BFF", fg="white", **btn_style, command=self.create_events).grid(row=0, column=0, pady=10)
        tk.Button(btn_frame, text="Add Students", bg="#007BFF", fg="white", **btn_style, command=self.add_students).grid(row=1, column=0, pady=10)
        tk.Button(btn_frame, text="Provide Feedback", bg="#007BFF", fg="white", **btn_style, command=self.provide_feedback).grid(row=2, column=0, pady=10)
        tk.Button(btn_frame, text="Logout", bg="#DC3545", fg="white", **btn_style, command=self.logout).grid(row=3, column=0, pady=10)


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
                user_id = self.user_id

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
        create_win.geometry(f"{create_win.winfo_screenwidth()}x{create_win.winfo_screenheight()}")
        create_win.state("zoomed")  # Set the window to full screen
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
        add_win = tk.Toplevel(self.root)
        add_win.title("Add Students")
        add_win.geometry(f"{add_win.winfo_screenwidth()}x{add_win.winfo_screenheight()}")
        add_win.state("zoomed")  # Set the window to full screen
        add_win.configure(bg="white")

        tk.Label(add_win, text="Add Students", font=("Arial", 16, "bold"), bg="white").pack(pady=10)

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

        event_var.trace_add("write", on_event_select)

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
        ).pack(pady=20)


    # ----------------------------------------------------
    # 3. Provide Feedback
    # ----------------------------------------------------
    # Helper function to underline text using Unicode combining underline
    def underline_text(text):
        return "".join([char + "\u0332" for char in text])

    def provide_feedback(self):
        """
        Opens a window for the teacher to:
        (a) Select a student assignment in the format StudentID - Student Name - EventID - Event Name.
        (b) Load and display that student’s file details (FileID, FileName, Format, Size in KB, Download)
            from the database.
        (c) Enter feedback in a large text box.
        (d) Approve or Decline the submission, updating the file status in the database accordingly.
        """
        feedback_win = tk.Toplevel(self.root)
        feedback_win.title("Provide Feedback")
        feedback_win.geometry(f"{feedback_win.winfo_screenwidth()}x{feedback_win.winfo_screenheight()}")
        feedback_win.state("zoomed")  # Set the window to full screen
        feedback_win.configure(bg="white")

        # -- Top Section: Fetch assignments dynamically for this teacher --
        top_label = tk.Label(feedback_win, text="Select Assignment", font=("Arial", 14, "bold"), bg="white")
        top_label.pack(pady=10)

        top_frame = tk.Frame(feedback_win, bg="white", padx=20, pady=10)
        top_frame.pack()

        tk.Label(top_frame, text="Assignment:", font=("Arial", 12), bg="white").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.assignment_var = tk.StringVar(value="Select Assignment")
        try:
            query = """
                SELECT ep.UserID, u.UserName, ep.EventID, e.EventName 
                FROM Event_Participation ep
                JOIN Users u ON ep.UserID = u.UserID
                JOIN Events e ON ep.EventID = e.EventID
                WHERE e.UserID = %s
                ORDER BY e.EventDate
            """
            self.cursor.execute(query, (self.user_id,))
            assignments_data = self.cursor.fetchall()
            assignments = [f"{row[0]} - {row[1]} - {row[2]} - {row[3]}" for row in assignments_data]
        except Exception as e:
            messagebox.showerror("Error", f"Error fetching assignments: {e}")
            assignments = []
        assignment_menu = ttk.Combobox(top_frame, textvariable=self.assignment_var, values=assignments, state="readonly", width=50)
        assignment_menu.grid(row=0, column=1, padx=5, pady=5)

        tk.Button(top_frame, text="Load Files", font=("Arial", 12, "bold"), bg="#007BFF", fg="white", command=self.load_files).grid(row=0, column=2, padx=10, pady=5)

        # -- Middle Section: Display File Details --
        self.files_tree = ttk.Treeview(feedback_win, columns=("FileID", "FileName", "Format", "Size", "Download"), show="headings", height=10)
        self.files_tree.heading("FileID", text="File ID")
        self.files_tree.heading("FileName", text="File Name")
        self.files_tree.heading("Format", text="Format")
        self.files_tree.heading("Size", text="Size (KB)")
        self.files_tree.heading("Download", text="Download")
        self.files_tree.column("FileID", width=80)
        self.files_tree.column("FileName", width=250)
        self.files_tree.column("Format", width=80)
        self.files_tree.column("Size", width=80)
        self.files_tree.column("Download", width=100)
        self.files_tree.pack(padx=20, pady=10)

        # Bind click event to detect clicks on the Download column.
        self.files_tree.bind("<Button-1>", self.on_tree_click)

        # -- Bottom Section: Enter Feedback --
        bottom_label = tk.Label(feedback_win, text="Enter Feedback", font=("Arial", 14, "bold"), bg="white")
        bottom_label.pack(pady=10)

        feedback_frame = tk.Frame(feedback_win, bg="white", padx=20, pady=10)
        feedback_frame.pack()
        self.feedback_text = tk.Text(feedback_frame, font=("Arial", 12), width=100, height=10, bd=2, relief="sunken")
        self.feedback_text.pack(pady=5)

        # Approve / Decline Buttons
        btn_frame = tk.Frame(feedback_win, bg="white")
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Approve", font=("Arial", 12, "bold"), bg="#28A745", fg="white", width=15, command=lambda: self.update_file_status("Approved")).grid(row=0, column=0, padx=10)
        tk.Button(btn_frame, text="Decline", font=("Arial", 12, "bold"), bg="#DC3545", fg="white", width=15, command=lambda: self.update_file_status("Declined")).grid(row=0, column=1, padx=10)

    def on_tree_click(self, event):
        """
        Handler for clicks on the Treeview. If the click is on the 'Download' column,
        download and open the file.
        """
        region = self.files_tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.files_tree.identify_column(event.x)
            # Check if click is on the 5th column ("#5") which is Download
            if column == "#5":
                item = self.files_tree.identify_row(event.y)
                if item:
                    file_id = self.files_tree.item(item)['values'][0]
                    self.download_file(file_id)

    def load_files(self):
        """
        Loads the file records from the database for the selected assignment.
        Displays the FileID, FileName, fixed 'PDF' format, file size (in KB),
        and an underlined 'Download' option in the Treeview.
        """
        # Clear existing rows
        for item in self.files_tree.get_children():
            self.files_tree.delete(item)

        assignment = self.assignment_var.get()
        if assignment == "Select Assignment":
            messagebox.showerror("Error", "Please select an assignment.")
            return

        try:
            parts = assignment.split("-")
            student_id = parts[0].strip()
            event_id = parts[2].strip()
        except Exception as e:
            messagebox.showerror("Error", f"Error parsing assignment: {e}")
            return

        try:
            query = """
                SELECT FileID, FileName, 'PDF' AS Format, COALESCE(ROUND(LENGTH(FileContent)/1024.0), 0) AS Size
                FROM Event_Files
                WHERE EventID = %s AND UserID = %s
            """
            self.cursor.execute(query, (event_id, student_id))
            results = self.cursor.fetchall()
            if results:
                for row in results:
                    self.files_tree.insert("", tk.END, values=(row[0], row[1], row[2], str(row[3]), "Download"))
            else:
                messagebox.showinfo("Load Files", "No files found for the selected assignment.")
        except Exception as e:
            messagebox.showerror("Error", f"Error loading files: {e}")

    def download_file(self, file_id):
        """
        Downloads the file with the given FileID from the database,
        saves it locally in the 'downloads' folder (at the project root), and opens it.
        """
        try:
            query = "SELECT FileName, FileContent FROM Event_Files WHERE FileID = %s"
            self.cursor.execute(query, (file_id,))
            result = self.cursor.fetchone()
            if result:
                file_name, file_content = result
                download_dir = os.path.join(PROJECT_ROOT, "downloads")
                if not os.path.exists(download_dir):
                    os.makedirs(download_dir)
                file_path = os.path.join(download_dir, file_name)
                with open(file_path, "wb") as f:
                    f.write(file_content)
                os.startfile(file_path)
            else:
                messagebox.showerror("Error", "File not found in database.")
        except Exception as e:
            messagebox.showerror("Error", f"Error downloading file: {e}")

    def update_file_status(self, status):
        """
        Updates the FileApprovalStatus of the selected file in the Event_Files table to 'Approved' or 'Declined'.
        Also, updates the feedback (if any) from the text box using the generate_unique_feedback function.
        """
        selected_item = self.files_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a file from the list.")
            return
        file_id = self.files_tree.item(selected_item)['values'][0]
        feedback_text = self.feedback_text.get("1.0", tk.END).strip()

        try:
            # Update file status
            query = "UPDATE Event_Files SET FileApprovalStatus = %s WHERE FileID = %s"
            self.cursor.execute(query, (status, file_id))

            # Insert feedback into Feedback table
            if feedback_text:
                from database.queries import generate_unique_feedback
                feedback_id = generate_unique_feedback()
                feedback_query = """
                    INSERT INTO Feedback (FeedbackID, FileID, UserID, Feedback)
                    VALUES (%s, %s, %s, %s)
                """
                self.cursor.execute(feedback_query, (feedback_id, file_id, self.user_id, feedback_text))

            self.conn.commit()
            messagebox.showinfo("Success", f"File status updated to {status}.")
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Error", f"Failed to update file status: {e}")


    # ----------------------------------------------------
    # 4. Logout
    # ----------------------------------------------------
    def logout(self):
        self.root.destroy()
        from pages.login_page import LoginPage
        root = tk.Tk()
        root.state("zoomed")  # Ensure the login page opens in full screen
        LoginPage(root)
        root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    root.state("zoomed")  # Open the teacher page in full screen
    TeacherDashboard(root)
    root.mainloop()
