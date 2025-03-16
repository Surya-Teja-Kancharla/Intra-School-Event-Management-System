import tkinter as tk
import sys
import os

# Add the pages directory to the Python path
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
PAGES_DIR = os.path.join(PROJECT_ROOT, "pages")
sys.path.append(PAGES_DIR)

# Import the LoginPage class from login_page.py
from pages.login_page import LoginPage

def main():
    """
    Main entry point of the application.
    Launches the login page in full-screen mode.
    """
    root = tk.Tk()
    root.title("Intra-School Event Management System")
    root.state("zoomed")  # Set the window to full screen
    root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}")
    LoginPage(root)  # Initialize the login page
    root.mainloop()

if __name__ == "__main__":
    main()
