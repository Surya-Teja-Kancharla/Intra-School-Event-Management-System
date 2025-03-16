import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime
from tkinter import ttk
import sys
import os
from database.db_connection import get_connection
from database.queries import generate_unique_file_id

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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
        Creates the main Student Dashboard with 3 buttons:
        1. View Events
        2. Upload Files
        3. Logout
        """
        header = tk.Label(self.root, text="Student Dashboard", font=("Arial", 18, "bold"), bg="#f0f0f0")
        header.pack(pady=20)

        btn_frame = tk.Frame(self.root, bg="#f0f0f0")
        btn_frame.pack(pady=10)

        btn_style = {"font": ("Arial", 12), "width": 25, "bd": 2, "relief": "raised"}

        tk.Button(btn_frame, text="View Events", bg="#007BFF", fg="white", **btn_style, command=self.view_events).grid(row=0, column=0, pady=10)
        tk.Button(btn_frame, text="Upload Files", bg="#007BFF", fg="white", **btn_style, command=self.upload_files).grid(row=1, column=0, pady=10)
        tk.Button(btn_frame, text="Logout", bg="#DC3545", fg="white", **btn_style, command=self.logout).grid(row=2, column=0, pady=10)

    def fetch_student_events(self):
        """
        Fetch events associated with the logged-in student.
        Now returns (EventID, EventName, EventDate).
        """
        try:
            query = """
                SELECT e.EventID, e.EventName, e.EventDate 
                FROM Events e
                JOIN Event_Participation ep ON e.EventID = ep.EventID
                WHERE TRIM(LOWER(ep.UserID)) = LOWER(TRIM(%s))
            """
            self.cursor.execute(query, (self.user_id,))
            results = self.cursor.fetchall()
            return results
        except Exception as e:
            messagebox.showerror("Error", f"Error fetching events: {e}")
            return []

    def view_events(self):
        """
        Opens a window with:
        - A calendar that color-codes events (completed/upcoming/current) for the logged-in student.
        - A text box that displays the event names on the selected day.
        """
        view_win = tk.Toplevel(self.root)
        view_win.title("View Events")
        view_win.geometry("700x500")
        view_win.configure(bg="white")

        # Title label
        tk.Label(view_win, text="View Events", font=("Arial", 16, "bold"), bg="white").pack(pady=10)

        # Calendar Section
        calendar_frame = tk.Frame(view_win, bg="white")
        calendar_frame.pack(pady=10, fill="x")

        from tkcalendar import Calendar
        calendar = Calendar(calendar_frame, selectmode='day', date_pattern="yyyy-mm-dd", font=("Arial", 12))
        calendar.pack(padx=20, pady=10, expand=True, fill="x")

        today_date = datetime.today().date()

        # Fetch events for this student
        events = self.fetch_student_events()

        for event_id, event_name, event_date in events:
            try:
                if isinstance(event_date, str):
                    ev_date = datetime.strptime(event_date, "%Y-%m-%d").date()
                else:
                    ev_date = event_date

                print(f"Creating calendar event: {event_name} on {ev_date}")  # Debug statement

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
                messagebox.showerror("Error", f"Error fetching events for the selected date: {e}")

        calendar.bind("<<CalendarSelected>>", on_date_select)

        
        
    # --------------------------------------------------
    # UPLOAD FILES
    # --------------------------------------------------
    def upload_files(self):
        """
        Opens a window where students can upload up to 3 files associated with an event.
        """
        upload_win = tk.Toplevel(self.root)
        upload_win.title("Upload Files")
        upload_win.geometry("500x600")
        upload_win.configure(bg="white")

        # Fetch events associated with the student
        events = self.fetch_student_events()

        tk.Label(upload_win, text="Select Event:", font=("Arial", 12), bg="white").pack(pady=10, anchor="w")
        selected_event = tk.StringVar(upload_win)
        # Format: "EventID - EventName (EventDate)"
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

            # "Drop files here" placeholder
            drop_frame = tk.Frame(section_frame, bg="#f0f0f0", width=300, height=60)
            drop_frame.pack(pady=5, fill="x")
            tk.Label(drop_frame, text="Drop files here\nOr", font=("Arial", 12), bg="#f0f0f0").pack(expand=True)

            # Browse button
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

        # Request Feedback button at the bottom
        tk.Button(
            upload_win,
            text="Request Feedback",
            font=("Arial", 12, "bold"),
            bg="#007BFF",
            fg="white",
            width=15,
            command=lambda: self.submit_files(selected_event.get(), file_entries)
        ).pack(pady=20)

    def submit_files(self, event_str, file_entries):
        """
        Submit the files to the database and save them locally in the uploads directory.
        """
        if not event_str:
            messagebox.showerror("Error", "Please select an event.")
            return

        # Extract EventID from the selected event string
        try:
            # Assuming the format "EventID - EventName (EventDate)"
            event_id = event_str.split(" - ")[0]
        except Exception as ex:
            messagebox.showerror("Error", f"Error parsing event details: {ex}")
            return

        for i, entry in enumerate(file_entries):
            file_name = entry.get().strip()
            if file_name:
                try:
                    file_path = os.path.join("uploads", file_name)
                    with open(file_path, "rb") as file_obj:
                        file_content = file_obj.read()

                    # Generate a unique FileID using the helper function
                    file_id = generate_unique_file_id()

                    query = """
                        INSERT INTO Event_Files (FileID, EventID, UserID, FileName, FileContent)
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    self.cursor.execute(query, (file_id, event_id, self.user_id, file_name, file_content))
                    self.conn.commit()

                    messagebox.showinfo("Success", f"File '{file_name}' uploaded successfully.")
                except Exception as e:
                    self.conn.rollback()
                    messagebox.showerror("Error", f"Failed to upload '{file_name}': {e}")

    def pick_pdf_file(self, entry_widget):
        """
        Opens a file dialog restricted to PDF files, updates the entry if valid.
        """
        file_path = filedialog.askopenfilename(
            title="Select a PDF File",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if file_path:
            # Check if file ends with .pdf
            if not file_path.lower().endswith(".pdf"):
                messagebox.showerror("Error", "Only PDF files are allowed.")
            else:
                if not os.path.exists("uploads"):
                    os.makedirs("uploads")
                dest_path = os.path.join("uploads", os.path.basename(file_path))
                with open(file_path, "rb") as src_file:
                    with open(dest_path, "wb") as dest_file:
                        dest_file.write(src_file.read())

                file_name = os.path.basename(file_path)
                entry_widget.delete(0, tk.END)
                entry_widget.insert(0, file_name)

    # --------------------------------------------------
    # LOGOUT
    # --------------------------------------------------
    def logout(self):
        """
        Logs the user out and returns to the login page.
        """
        self.root.destroy()
        from pages.login_page import LoginPage
        root = tk.Tk()
        LoginPage(root)
        root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    # Provide a valid student user ID
    StudentDashboard(root)
    root.mainloop()
