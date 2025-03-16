<h1>Intra-School Event Management Desktop Application</h1>

<h2><strong>Problem Statement</strong></h2>
<p>
Intra-School Event Management can be challenging, requiring efficient coordination between administrators, teachers, and students. 
This project aims to provide a streamlined desktop application to simplify event management, from registration to final results. 
The application ensures smooth communication and proper role-based access control.
</p>

---

<h2><strong>Project Overview</strong></h2>
<p>
This is a desktop application built using Python and PostgreSQL for the backend. 
It incorporates Object-Oriented Programming (OOP) principles, such as Classes, Objects, Data Abstraction, Inheritance, Polymorphism, and Encapsulation. 
The GUI modules handle role-based user interactions for Admins, Teachers, and Students. PostgreSQL is used to store and manage data.
</p>

---

<h2><strong>Directory Structure</strong></h2>
<pre>
Intra-School Event Management/
├── assets/                # Images, icons, and other assets for the UI
│   ├── Criteria A (1).pdf
│   ├── Criteria B CS IA 2(1).pdf
├── database/              # Contains all PostgreSQL-related operations
│   ├── __init__.py
│   ├── db_connection.py   # Handles connection with PostgreSQL
│   ├── schema.sql         # SQL file to create tables and schema
│   └── queries.py         # Optional file for common queries
├── downloads/
├── pages/                 # Contains all GUI-related modules (Login, Dashboards, etc.)
│   ├── __init__.py
│   ├── login_page.py
│   ├── admin_page.py
│   ├── teacher_page.py
│   └── student_page.py
├── uploads/
├── venv/                  # Virtual environment for the project
├── .env                   # Contains environment variables like database credentials
├── .gitignore             # Git configuration to ignore unnecessary files
├── main.py                # The entry point for your application
├── requirements.txt       # List of all required packages
├── test_queries.py        # Script for testing database queries
└── README.md              # Project documentation
</pre>

---

<h2><strong>Setup Instructions</strong></h2>

<h3><strong>Step 1: Clone the Repository</strong></h3>
<pre>
git clone &lt;repository-url&gt;
cd Intra-School Event Management
</pre>

<h3><strong>Step 2: Create a Virtual Environment</strong></h3>
<pre>
python -m venv venv
</pre>
<p>Activate the virtual environment:</p>
<ul>
  <li>On Windows:
    <pre>venv\Scripts\activate</pre>
  </li>
  <li>On macOS/Linux:
    <pre>source venv/bin/activate</pre>
  </li>
</ul>

<h3><strong>Step 3: Install Dependencies</strong></h3>
<pre>
pip install -r requirements.txt
</pre>

<h3><strong>Step 4: Set Up PostgreSQL</strong></h3>
<ol>
  <li>Install PostgreSQL and ensure it's running.</li>
  <li>Create a database named <code>Event_Management</code>.</li>
  <li>Open the <code>database/schema.sql</code> file and execute its content to create tables and schema:
    <pre>psql -U &lt;username&gt; -d Event_Management -f database/schema.sql</pre>
  </li>
</ol>

<h3><strong>Step 5: Configure Environment Variables</strong></h3>
<p>Create a <code>.env</code> file in the project root directory and add the following:</p>
<pre>
DB_NAME=Event_Management
DB_USER=&lt;your-username&gt;
DB_PASSWORD=&lt;your-password&gt;
DB_HOST=localhost
DB_PORT=5432
</pre>

<h3><strong>Step 6: Test Database Connection</strong></h3>
<pre>
python test_queries.py
</pre>

<h3><strong>Step 7: Build the Application</strong></h3>
<pre>
python main.py
</pre>
<p>The application will launch with the GUI for Admin, Teacher, and Student modules.</p>

---

<h2><strong>Convert Python Script to .exe File</strong></h2>

<h3><strong>Step 1: Install PyInstaller</strong></h3>
<pre>
pip install pyinstaller
</pre>

<h3><strong>Step 2: Generate the Executable File</strong></h3>
<p>Run the following command in the terminal:</p>
<pre>
pyinstaller --onefile --windowed main.py
</pre>
<p>This will create an executable file in the <code>dist</code> directory.</p>

<h3><strong>Step 3: Copy .exe File to Application Directory</strong></h3>
<p>Navigate to the <code>dist</code> directory:</p>
<pre>
cd dist
</pre>
<p>Copy the generated <code>main.exe</code> file to the project directory or a suitable location for deployment:</p>
<pre>
copy main.exe "C:\Path\To\Intra-School Event Management\"
</pre>

<h3><strong>Step 4: Place .exe File on Desktop</strong></h3>
<p>Move or copy the <code>main.exe</code> file to your desktop:</p>
<pre>
copy main.exe "C:\Users\<username>\Desktop"
</pre>

<h3><strong>Step 5: Run the Application</strong></h3>
<p>Double-click the <code>main.exe</code> file on your desktop to launch the Intra-School Event Management application.</p>

---

<h2><strong>Features</strong></h2>
<ul>
  <li><strong>Role-Based Access:</strong> Separate dashboards for Admins, Teachers, and Students.</li>
  <li><strong>Event Management:</strong> Allows Admins to create, update, and manage events.</li>
  <li><strong>Student Registration:</strong> Enables students to register for events and view results.</li>
  <li><strong>Reports:</strong> Teachers can upload event-related documents and evaluate submissions.</li>
</ul>

---

<h2><strong>Technologies Used</strong></h2>
<ul>
  <li><strong>Programming Language:</strong> Python</li>
  <li><strong>Database:</strong> PostgreSQL</li>
  <li><strong>GUI Framework:</strong> Tkinter</li>
  <li><strong>Environment Management:</strong> <code>venv</code></li>
</ul>

---

<h2><strong>How to Contribute</strong></h2>
<ol>
  <li>Fork the repository.</li>
  <li>Create a new branch:
    <pre>git checkout -b feature-name</pre>
  </li>
  <li>Commit your changes:
    <pre>git commit -m "Add your message"</pre>
  </li>
  <li>Push to the branch:
    <pre>git push origin feature-name</pre>
  </li>
  <li>Create a Pull Request.</li>
</ol>

---

<h2><strong>Contact</strong></h2>
<p>For any queries or feedback, feel free to reach out.</p>
