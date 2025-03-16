import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class StudentDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Dashboard - Intra-School Event Management")
        self.root.configure(bg="#f0f0f0")
        self.root.geometry("700x500")

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

        # 1. View Events (replacing the old "Dashboard" button)
        tk.Button(
            btn_frame,
            text="View Events",
            bg="#007BFF",
            fg="white",
            **btn_style,
            command=self.view_events
        ).grid(row=0, column=0, pady=10)

        # 2. Upload Files
        tk.Button(
            btn_frame,
            text="Upload Files",
            bg="#007BFF",
            fg="white",
            **btn_style,
            command=self.upload_files
        ).grid(row=1, column=0, pady=10)

        # 3. Logout
        tk.Button(
            btn_frame,
            text="Logout",
            bg="#DC3545",
            fg="white",
            **btn_style,
            command=self.logout
        ).grid(row=2, column=0, pady=10)

    # --------------------------------------------------
    # VIEW EVENTS (Combined Calendar + Event List)
    # --------------------------------------------------
    def view_events(self):
        """
        Opens a window with:
        - A calendar that color-codes events (completed/upcoming/current).
        - A list of events in a Listbox or Treeview.
        """
        view_win = tk.Toplevel(self.root)
        view_win.title("View Events")
        view_win.geometry("700x500")
        view_win.configure(bg="white")

        # Title
        tk.Label(view_win, text="View Events", font=("Arial", 16, "bold"), bg="white").pack(pady=10)

        # 1) Calendar Section
        calendar_frame = tk.Frame(view_win, bg="white")
        calendar_frame.pack(pady=10, fill="x")

        try:
            from tkcalendar import Calendar
            from datetime import datetime
        except ImportError:
            messagebox.showerror("Error", "tkcalendar not installed. Please install it to view the calendar.")
            return

        calendar = Calendar(calendar_frame, selectmode='none', date_pattern="yyyy-mm-dd", font=("Arial", 12))
        calendar.pack(padx=20, pady=10, expand=True, fill="x")

        # Dummy event data
        event_dates = [
            {"EventName": "Science Fair",   "EventDate": "2025-03-20"},
            {"EventName": "Sports Day",     "EventDate": "2025-04-15"},
            {"EventName": "Today’s Meeting","EventDate": datetime.today().strftime("%Y-%m-%d")},
            {"EventName": "Music Concert",  "EventDate": "2025-03-25"}
        ]

        today_date = datetime.today().date()
        for ev in event_dates:
            try:
                ev_date = datetime.strptime(ev["EventDate"], "%Y-%m-%d").date()
                if ev_date < today_date:
                    tag = "completed"  # Red
                elif ev_date > today_date:
                    tag = "upcoming"   # Green
                else:
                    tag = "current"    # Blue
                calendar.calevent_create(ev_date, ev["EventName"], tag)
            except Exception as ex:
                print(f"Error creating calendar event: {ex}")

        # Configure color tags
        calendar.tag_config("completed", background="red", foreground="white")
        calendar.tag_config("upcoming", background="green", foreground="white")
        calendar.tag_config("current", background="blue", foreground="white")

        # 2) List of Events
        tk.Label(view_win, text="Event List:", font=("Arial", 14, "bold"), bg="white").pack(pady=(10, 0))

        list_frame = tk.Frame(view_win, bg="white")
        list_frame.pack(pady=5, fill="both", expand=True)

        event_listbox = tk.Listbox(list_frame, font=("Arial", 12), width=50, height=6)
        event_listbox.pack(side="left", fill="both", expand=True, padx=10, pady=5)

        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=event_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        event_listbox.config(yscrollcommand=scrollbar.set)

        # Populate the listbox with the same dummy events
        for ev in event_dates:
            event_listbox.insert(tk.END, f"{ev['EventName']} on {ev['EventDate']}")

        tk.Label(view_win, text="(Red = Completed, Green = Upcoming, Blue = Current)", 
                 font=("Arial", 10), bg="white").pack(pady=(0, 10))

    # --------------------------------------------------
    # UPLOAD FILES
    # --------------------------------------------------
    def upload_files(self):
        """
        Opens a window where only PDF files can be uploaded.
        Three sections, each with "File Name", "Drop files here", and "Browse" button.
        A "Request Feedback" button at the bottom.
        """
        upload_win = tk.Toplevel(self.root)
        upload_win.title("Upload Files")
        upload_win.geometry("400x600")
        upload_win.configure(bg="white")

        tk.Label(upload_win, text="Upload Files", font=("Arial", 16, "bold"), bg="white").pack(pady=10)

        # Create 3 upload sections
        for i in range(1, 4):
            section_frame = tk.Frame(upload_win, bg="white", padx=10, pady=10, bd=1, relief="groove")
            section_frame.pack(pady=10, fill="x", expand=True)

            tk.Label(section_frame, text=f"File Name {i}:", font=("Arial", 12), bg="white").pack(anchor="w")
            file_name_entry = tk.Entry(section_frame, font=("Arial", 12), width=30)
            file_name_entry.pack(pady=5)

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
            command=lambda: messagebox.showinfo("Request Feedback", "Feedback requested (dummy)")
        ).pack(pady=20)

    def pick_pdf_file(self, entry_widget):
        """Opens a file dialog restricted to PDF files, updates the entry if valid."""
        file_path = filedialog.askopenfilename(
            title="Select a PDF File",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if file_path:
            # Check if file ends with .pdf
            if not file_path.lower().endswith(".pdf"):
                messagebox.showerror("Error", "File Type Not accepted")
            else:
                # Update the entry with the selected file's name
                file_name = os.path.basename(file_path)
                entry_widget.delete(0, tk.END)
                entry_widget.insert(0, file_name)

    # --------------------------------------------------
    # LOGOUT
    # --------------------------------------------------
    def logout(self):
        """Logs the user out and returns to the login page."""
        self.root.destroy()
        from pages.login_page import LoginPage
        root = tk.Tk()
        LoginPage(root)
        root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    StudentDashboard(root)
    root.mainloop()
