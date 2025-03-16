import os
import sys
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from datetime import datetime
from database.db_connection import get_connection

# Define project root (one level above the pages folder)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

class StudentDashboard:
    def __init__(self, root, user_id):
        self.root = root
        self.user_id = user_id
        self.root.title("Student Dashboard - Intra-School Event Management")
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
        Creates the main Student Dashboard with 4 buttons:
        1. View Events
        2. Upload Files
        3. View Feedback
        4. Logout
        """
        header = tk.Label(self.root, text="Student Dashboard", font=("Arial", 18, "bold"), bg="#f0f0f0")
        header.pack(pady=20)

        btn_frame = tk.Frame(self.root, bg="#f0f0f0")
        btn_frame.pack(pady=10)

        btn_style = {"font": ("Arial", 12), "width": 25, "bd": 2, "relief": "raised"}

        tk.Button(btn_frame, text="View Events", bg="#007BFF", fg="white", **btn_style, command=self.view_events).grid(row=0, column=0, pady=10)
        tk.Button(btn_frame, text="Upload Files", bg="#007BFF", fg="white", **btn_style, command=self.upload_files).grid(row=1, column=0, pady=10)
        tk.Button(btn_frame, text="View Feedback", bg="#007BFF", fg="white", **btn_style, command=self.view_feedback).grid(row=2, column=0, pady=10)
        tk.Button(btn_frame, text="Logout", bg="#DC3545", fg="white", **btn_style, command=self.logout).grid(row=3, column=0, pady=10)

    def fetch_student_events(self):
        """
        Fetches events associated with the logged-in student.
        Returns a list of tuples (EventID, EventName, EventDate).
        """
        try:
            query = """
                SELECT e.EventID, e.EventName, e.EventDate 
                FROM Events e
                JOIN Event_Participation ep ON e.EventID = ep.EventID
                WHERE TRIM(LOWER(ep.UserID)) = LOWER(TRIM(%s))
            """
            self.cursor.execute(query, (self.user_id,))
            return self.cursor.fetchall()
        except Exception as e:
            messagebox.showerror("Error", f"Error fetching events: {e}")
            return []

    def view_events(self):
        """
        Opens a window to display a calendar and event details.
        (Existing implementation remains unchanged.)
        """
        view_win = tk.Toplevel(self.root)
        view_win.title("View Events")
        view_win.geometry("700x500")
        view_win.configure(bg="white")

        tk.Label(view_win, text="View Events", font=("Arial", 16, "bold"), bg="white").pack(pady=10)

        # Calendar Section
        calendar_frame = tk.Frame(view_win, bg="white")
        calendar_frame.pack(pady=10, fill="x")

        from tkcalendar import Calendar
        calendar = Calendar(calendar_frame, selectmode='day', date_pattern="yyyy-mm-dd", font=("Arial", 12))
        calendar.pack(padx=20, pady=10, expand=True, fill="x")

        today_date = datetime.today().date()
        events = self.fetch_student_events()
        for event_id, event_name, event_date in events:
            try:
                if isinstance(event_date, str):
                    ev_date = datetime.strptime(event_date, "%Y-%m-%d").date()
                else:
                    ev_date = event_date
                if ev_date < today_date:
                    tag = "completed"
                elif ev_date > today_date:
                    tag = "upcoming"
                else:
                    tag = "current"
                calendar.calevent_create(ev_date, event_name, tag)
            except Exception as ex:
                print(f"Error creating calendar event: {ex}")

        calendar.tag_config("completed", background="red", foreground="white")
        calendar.tag_config("upcoming", background="green", foreground="white")
        calendar.tag_config("current", background="blue", foreground="white")

        tk.Label(view_win, text="Event dates are highlighted on the calendar.", font=("Arial", 12), bg="white").pack(pady=10)

        event_details = tk.Text(view_win, height=5, width=60, font=("Arial", 12), state="disabled")
        event_details.pack(pady=10)

        def on_date_select(event):
            selected_date = calendar.get_date()  # Format: yyyy-mm-dd
            try:
                query = """
                    SELECT e.EventName 
                    FROM Events e
                    JOIN Event_Participation ep ON e.EventID = ep.EventID
                    WHERE TRIM(LOWER(ep.UserID)) = LOWER(TRIM(%s)) AND e.EventDate = %s
                """
                self.cursor.execute(query, (self.user_id, selected_date))
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
                messagebox.showerror("Error", f"Error fetching events: {e}")

        calendar.bind("<<CalendarSelected>>", on_date_select)

    def upload_files(self):
        """
        Opens a window where students can upload up to 3 files associated with an event.
        (Existing implementation remains unchanged.)
        """
        upload_win = tk.Toplevel(self.root)
        upload_win.title("Upload Files")
        upload_win.geometry("500x600")
        upload_win.configure(bg="white")

        events = self.fetch_student_events()
        tk.Label(upload_win, text="Select Event:", font=("Arial", 12), bg="white").pack(pady=10, anchor="w")
        selected_event = tk.StringVar(upload_win)
        event_options = [f"{row[0]} - {row[1]} ({row[2]})" for row in events]
        tk.OptionMenu(upload_win, selected_event, *event_options).pack(pady=5, anchor="w")

        file_entries = []
        for i in range(1, 4):
            section_frame = tk.Frame(upload_win, bg="white", padx=10, pady=10, bd=1, relief="groove")
            section_frame.pack(pady=10, fill="x", expand=True)
            tk.Label(section_frame, text=f"File Name {i}:", font=("Arial", 12), bg="white").pack(anchor="w")
            file_name_entry = tk.Entry(section_frame, font=("Arial", 12), width=30)
            file_name_entry.pack(pady=5)
            file_entries.append(file_name_entry)

            drop_frame = tk.Frame(section_frame, bg="#f0f0f0", width=300, height=60)
            drop_frame.pack(pady=5, fill="x")
            tk.Label(drop_frame, text="Drop files here\nOr", font=("Arial", 12), bg="#f0f0f0").pack(expand=True)

            browse_button = tk.Button(
                section_frame,
                text="Browse",
                font=("Arial", 12, "bold"),
                bg="#007BFF",
                fg="white",
                width=10,
                command=lambda e=file_name_entry: self.pick_pdf_file(e)
            )
            browse_button.pack(pady=5)

        tk.Button(
            upload_win,
            text="Request Feedback",
            font=("Arial", 12, "bold"),
            bg="#007BFF",
            fg="white",
            width=15,
            command=lambda: self.submit_files(selected_event.get(), file_entries)
        ).pack(pady=20)

    def pick_pdf_file(self, entry_widget):
        """
        Opens a file dialog restricted to PDF files, updates the entry if valid.
        """
        file_path = filedialog.askopenfilename(
            title="Select a PDF File",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if file_path:
            if not file_path.lower().endswith(".pdf"):
                messagebox.showerror("Error", "Only PDF files are allowed.")
            else:
                uploads_dir = os.path.join(PROJECT_ROOT, "uploads")
                if not os.path.exists(uploads_dir):
                    os.makedirs(uploads_dir)
                dest_path = os.path.join(uploads_dir, os.path.basename(file_path))
                with open(file_path, "rb") as src_file:
                    with open(dest_path, "wb") as dest_file:
                        dest_file.write(src_file.read())
                file_name = os.path.basename(file_path)
                entry_widget.delete(0, tk.END)
                entry_widget.insert(0, file_name)

    def submit_files(self, event_str, file_entries):
        """
        Submits the files to the database and saves them locally in the uploads directory.
        Updates the file record with FileApprovalStatus set to "Pending".
        """
        if not event_str:
            messagebox.showerror("Error", "Please select an event.")
            return

        try:
            event_id = event_str.split(" - ")[0]
        except Exception as ex:
            messagebox.showerror("Error", f"Error parsing event details: {ex}")
            return

        for entry in file_entries:
            file_name = entry.get().strip()
            if file_name:
                try:
                    uploads_dir = os.path.join(PROJECT_ROOT, "uploads")
                    if not os.path.exists(uploads_dir):
                        os.makedirs(uploads_dir)
                    file_path = os.path.join(uploads_dir, file_name)
                    with open(file_path, "rb") as file_obj:
                        file_content = file_obj.read()

                    from database.queries import generate_unique_file_id
                    file_id = generate_unique_file_id()

                    query = """
                        INSERT INTO Event_Files (FileID, EventID, UserID, FileName, FileContent, FileApprovalStatus)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    self.cursor.execute(query, (file_id, event_id, self.user_id, file_name, file_content, "Pending"))
                    self.conn.commit()

                    messagebox.showinfo("Success", f"File '{file_name}' uploaded successfully.")
                except Exception as e:
                    self.conn.rollback()
                    messagebox.showerror("Error", f"Failed to upload '{file_name}': {e}")

    def view_feedback(self):
        """
        Opens a window for the student to view feedback for a selected event.
        The student sees a dropdown populated with their events in the format:
        "EventID-EventName-TeacherName", where TeacherName is the username of the teacher who created the event.
        Below the dropdown, a text area displays the feedback given by the teacher along with the file status (Approved/Declined/Pending).
        """
        feedback_win = tk.Toplevel(self.root)
        feedback_win.title("View Feedback")
        feedback_win.geometry("600x500")
        feedback_win.configure(bg="white")

        # Top Section: Label and dropdown for events
        top_frame = tk.Frame(feedback_win, bg="white", padx=20, pady=10)
        top_frame.pack(pady=10)
        tk.Label(top_frame, text="Select Event:", font=("Arial", 12), bg="white").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.feedback_event_var = tk.StringVar(value="Select Event")
        try:
            # Fetch events for the logged-in student along with the teacher name
            query = """
                SELECT e.EventID, e.EventName, u.UserName
                FROM Events e
                JOIN Event_Participation ep ON e.EventID = ep.EventID
                JOIN Users u ON e.UserID = u.UserID
                WHERE TRIM(LOWER(ep.UserID)) = LOWER(TRIM(%s))
            """
            self.cursor.execute(query, (self.user_id,))
            events_data = self.cursor.fetchall()
            # Format: "EventID-EventName-TeacherName"
            events_list = [f"{row[0]}-{row[1]}-{row[2]}" for row in events_data]
        except Exception as e:
            messagebox.showerror("Error", f"Error fetching events: {e}")
            events_list = []
        event_menu = ttk.Combobox(top_frame, textvariable=self.feedback_event_var, values=events_list, state="readonly", width=40)
        event_menu.grid(row=0, column=1, padx=5, pady=5)

        # Button to load feedback for the selected event
        tk.Button(top_frame, text="Load Feedback", font=("Arial", 12, "bold"), bg="#007BFF", fg="white",
                  command=self.load_feedback).grid(row=0, column=2, padx=10, pady=5)

        # Bottom Section: Label and text area for displaying feedback and file status
        bottom_label = tk.Label(feedback_win, text="Feedback Given", font=("Arial", 14, "bold"), bg="white")
        bottom_label.pack(pady=10)
        self.feedback_display = tk.Text(feedback_win, font=("Arial", 12), width=70, height=15, bd=2, relief="sunken", state="disabled")
        self.feedback_display.pack(padx=20, pady=10)

    def load_feedback(self):
        """
        Loads and displays the teacher feedback and file status for the selected event.
        """
        event_str = self.feedback_event_var.get()
        if event_str == "Select Event":
            messagebox.showerror("Error", "Please select an event.")
            return

        try:
            # Expected format: "EventID-EventName-TeacherName"
            parts = event_str.split("-")
            event_id = parts[0].strip()
        except Exception as e:
            messagebox.showerror("Error", f"Error parsing event details: {e}")
            return

        try:
            query = """
                SELECT f.Feedback, ef.FileApprovalStatus
                FROM Feedback f
                JOIN Event_Files ef ON f.FileID = ef.FileID
                WHERE ef.EventID = %s AND ef.UserID = %s
            """
            self.cursor.execute(query, (event_id, self.user_id))
            feedback_results = self.cursor.fetchall()

            self.feedback_display.config(state="normal")
            self.feedback_display.delete("1.0", tk.END)
            if feedback_results:
                for feedback, status in feedback_results:
                    self.feedback_display.insert(tk.END, f"Status: {status}\nFeedback: {feedback}\n\n")
            else:
                self.feedback_display.insert(tk.END, "No feedback found for the selected event.")
            self.feedback_display.config(state="disabled")
        except Exception as e:
            messagebox.showerror("Error", f"Error loading feedback: {e}")


    def logout(self):
        self.root.destroy()
        from pages.login_page import LoginPage
        root = tk.Tk()
        LoginPage(root)
        root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    StudentDashboard(root)
    root.mainloop()
