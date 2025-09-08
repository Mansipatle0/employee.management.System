Employee Management System (EMS)



The Employee Management System (EMS) is a web-based application developed using Django and Python. It facilitates efficient management of employees, interns, attendance, leave requests, and user roles (Admin, HR, Employee, Intern).


---

🚀 Features

Role-Based Authentication: Secure login for Admin, HR, Employee, and Intern.

Attendance Tracking: Monitor check-in/check-out times and calculate working hours.

Leave Management: Apply, approve, or reject leave requests.

Role-Specific Dashboards: Tailored interfaces for different user roles.

Responsive UI: Built with HTML, CSS, and Tailwind for a modern look.



---

🛠️ Tech Stack

Backend: Django, Python

Frontend: HTML, CSS, Tailwind

Database: SQLite (default)

Deployment: Compatible with Heroku and PythonAnywhere



---

📂 Project Structure

Employee-Management-System/
│── emp/                # Main Django app
│── templates/          # HTML templates
│── static/             # Static files (CSS, JS)
│── manage.py           # Django project manager
│── db.sqlite3          # Default database
│── requirements.txt    # Project dependencies



⚡ How to Run Locally

1. Clone the repository:

git clone https://github.com/Mansipatle0/employee.management.System.git
cd employee.management.System


2. Set up a virtual environment:

python -m venv venv
source venv/bin/activate   # for Linux/Mac
venv\Scripts\activate      # for Windows


3. Install dependencies:

pip install -r requirements.txt


4. Apply migrations:

python manage.py migrate


5. Run the development server:

python manage.py runserver

Visit the app at http://127.0.0.1:8000/




---

💡 Optional Setup Tips

Create a superuser for Admin access:

python manage.py createsuperuser

Collect static files for deployment:

python manage.py collectstatic

Ensure DEBUG = True in settings.py for local development.



---

👩‍💻 Author

Name: Mansi Patle
GitHub: Mansipatle0
