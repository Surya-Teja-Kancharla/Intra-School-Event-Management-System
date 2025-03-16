import tkinter as tk
from tkinter import messagebox
import sys
import os

# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the database connection module
from database.db_connection import get_connection

class LoginPage:
    def __init__(self, root):
        self.root = root
        self.root.title("Intra-School Event Management - Login")
        self.root.configure(bg="#f0f0f0")  # Light gray background
        self.root.geometry("450x350")

        # Placeholder strings
        self.username_placeholder = "Enter Username"
        self.password_placeholder = "Enter Password"

        self.create_widgets()

    def create_widgets(self):
        """
        Creates the UI elements for the login page, including placeholder text for
        username and password fields.
        """

        # Frame for the login area (white background, with a groove border)
        login_frame = tk.Frame(self.root, bg="white", padx=20, pady=20, bd=2, relief="groove")
        login_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Title label
        title = tk.Label(login_frame, text="User Login", font=("Arial", 16, "bold"), bg="white")
        title.grid(row=0, column=0, columnspan=2, pady=(0, 15))

        # Username label
        tk.Label(login_frame, text="Username:", font=("Arial", 12), bg="white").grid(
            row=1, column=0, sticky="e", padx=(0, 10), pady=5
        )
        # Username Entry
        self.username_entry = tk.Entry(login_frame, font=("Arial", 12), width=25, bd=2, relief="sunken")
        self.username_entry.grid(row=1, column=1, pady=5)
        self.set_placeholder(self.username_entry, self.username_placeholder)
        # Bind focus events
        self.username_entry.bind("<FocusIn>", lambda event: self.clear_placeholder(event, self.username_placeholder))
        self.username_entry.bind("<FocusOut>", lambda event: self.restore_placeholder(event, self.username_placeholder))

        # Password label
        tk.Label(login_frame, text="Password:", font=("Arial", 12), bg="white").grid(
            row=2, column=0, sticky="e", padx=(0, 10), pady=5
        )
        # Password Entry
        self.password_entry = tk.Entry(login_frame, font=("Arial", 12), width=25, bd=2, relief="sunken")
        self.password_entry.grid(row=2, column=1, pady=5)
        self.set_placeholder(self.password_entry, self.password_placeholder)
        # Bind focus events
        self.password_entry.bind("<FocusIn>", lambda event: self.clear_placeholder(event, self.password_placeholder, is_password=True))
        self.password_entry.bind("<FocusOut>", lambda event: self.restore_placeholder(event, self.password_placeholder, is_password=True))

        # Role label
        tk.Label(login_frame, text="Role:", font=("Arial", 12), bg="white").grid(
            row=3, column=0, sticky="e", padx=(0, 10), pady=5
        )
        self.role_var = tk.StringVar(value="Select Role")
        roles = ["Admin", "Teacher", "Student"]
        role_menu = tk.OptionMenu(login_frame, self.role_var, *roles)
        role_menu.config(font=("Arial", 12), width=22)
        role_menu.grid(row=3, column=1, sticky="w", pady=5)

        # Submit/Login button (blue background)
        login_button = tk.Button(
            login_frame,
            text="Submit",
            font=("Arial", 12, "bold"),
            bg="#007BFF",     # Blue background
            fg="white",
            width=20,
            command=self.login
        )
        login_button.grid(row=4, column=0, columnspan=2, pady=(15, 0))

    def set_placeholder(self, entry_widget, placeholder_text):
        """
        Inserts placeholder text into the entry widget if it is empty.
        """
        entry_widget.insert(0, placeholder_text)
        entry_widget.config(fg="grey")

    def clear_placeholder(self, event, placeholder_text, is_password=False):
        """
        Clears the placeholder text upon focusing in. If this is the password field,
        also updates the entry to show '*' instead of plain text.
        """
        widget = event.widget
        if widget.get() == placeholder_text:
            widget.delete(0, tk.END)
            widget.config(fg="black")
            if is_password:
                widget.config(show="*")

    def restore_placeholder(self, event, placeholder_text, is_password=False):
        """
        Restores placeholder text if the user leaves the entry box empty.
        """
        widget = event.widget
        if widget.get() == "":
            widget.config(fg="grey")
            widget.insert(0, placeholder_text)
            if is_password:
                widget.config(show="")

    def login(self):
        """
        Fetches the credentials, validates them from the database, and navigates
        to the relevant dashboard page based on the role.
        """
        username = self.username_entry.get()
        password = self.password_entry.get()
        role = self.role_var.get()

        # If placeholders are still there, treat them as empty
        if username == self.username_placeholder:
            username = ""
        if password == self.password_placeholder:
            password = ""

        if role == "Select Role":
            messagebox.showerror("Error", "Please select a role.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            query = """
                SELECT UserID, UserRole FROM Users
                WHERE UserName = %s AND UserPass = %s AND UserRole = %s
            """
            cursor.execute(query, (username, password, role))
            result = cursor.fetchone()

            if result:
                user_id, user_role = result
                messagebox.showinfo("Success", f"Welcome, {role}!")
                self.navigate_to_dashboard(role, user_id)
            else:
                messagebox.showerror("Error", "Invalid credentials or role")
            
            cursor.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {e}")

    def navigate_to_dashboard(self, role, user_id):
        """
        Closes the current window and opens the role-specific dashboard.
        Passes the `user_id` to the relevant dashboard.
        """
        self.root.destroy()
        if role == "Admin":
            from pages.admin_page import AdminDashboard
            root = tk.Tk()
            AdminDashboard(root, user_id)
            root.mainloop()
        elif role == "Teacher":
            from pages.teacher_page import TeacherDashboard
            root = tk.Tk()
            TeacherDashboard(root, user_id)  # Pass `user_id` to TeacherDashboard
            root.mainloop()
        elif role == "Student":
            from pages.student_page import StudentDashboard
            root = tk.Tk()
            StudentDashboard(root, user_id)  # Pass `user_id` to StudentDashboard
            root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    LoginPage(root)
    root.mainloop()
