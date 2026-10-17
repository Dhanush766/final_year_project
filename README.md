# Employee Management System

A responsive web application for managing employee records, built with **Python, Django, MySQL, HTML, CSS, Bootstrap 5 and JavaScript**. The user interface is rendered by Django templates (there is no separate frontend application).

> **Verification status (please read):** Automated tests are included in `employees/tests/`, and the code was syntax-checked and cross-checked for consistent URL names, template references and imports. The test-suite and the running application were **not executed** by the person who generated this project (Django could not be installed in that environment). Follow the "Run the tests" and "Manual verification checklist" sections on your own machine and record your results in the table at the end of this file.

---

## 1. Features

| # | Feature | Where |
|---|---------|-------|
| 1 | Admin login / logout (Django authentication) | `/login/`, `/logout/` |
| 2 | Dashboard: total, active, not-active employees, department statistics | `/` |
| 3 | Add employee | `/employees/add/` |
| 4 | View all employees (paginated, 10 per page) | `/employees/` |
| 5 | View employee details | `/employees/<id>/` |
| 6 | Update employee | `/employees/<id>/edit/` |
| 7 | Delete employee with confirmation page | `/employees/<id>/delete/` |
| 8 | Search by name and employee ID | search box on `/employees/` |
| 9 | Filter by department and employment status | drop-downs on `/employees/` |
| 10 | Department management (list, add, edit, delete) | `/departments/` |
| 11 | Form validation (server-side, plus browser hints) | `forms.py`, `validators.py` |
| 12 | Success and error messages | Django messages framework |
| 13 | Responsive Bootstrap 5 interface | `templates/`, `static/` |
| 14 | MySQL integration | `config/settings.py` |
| 15 | Django Admin integration | `/admin/`, `employees/admin.py` |
| 16 | Automated tests | `employees/tests/` |
| 17 | Access control (login + permissions, CSRF) | `views.py` |
| 18 | Error handling (403, 404, 500 pages, protected deletes, safe filters) | `templates/`, `views.py` |

### Roles and permissions

Every page requires login **and** a Django permission. Superusers have everything. Two ready-made groups are created by `python manage.py setup_roles`:

| Role | View | Add | Edit | Delete |
|------|------|-----|------|--------|
| Superuser | yes | yes | yes | yes |
| HR Manager (group) | yes | yes | yes | yes |
| Viewer (group) | yes | no | no | no |
| Any other logged-in user | no (403 page) | no | no | no |

Only users with **Staff status** can open the Django Admin site.

---

## 2. Folder structure

```
ems_project/
|-- manage.py
|-- requirements.txt
|-- .env.example              <- template for your private .env file
|-- .gitignore
|-- README.md
|-- docs/
|   `-- PROJECT_GUIDE.md      <- architecture, report outline, demo script, interview Q&A
|-- config/                   <- project settings package
|   |-- settings.py
|   |-- urls.py
|   |-- wsgi.py
|   `-- asgi.py
|-- employees/                <- the application
|   |-- models.py             <- Department, Employee
|   |-- validators.py         <- reusable validation functions
|   |-- forms.py              <- EmployeeForm, DepartmentForm, filter form, login form
|   |-- views.py              <- all pages + access control
|   |-- urls.py               <- named URL patterns (namespace "employees")
|   |-- admin.py              <- Django Admin configuration
|   |-- context_processors.py
|   |-- migrations/0001_initial.py
|   |-- management/commands/
|   |   |-- setup_roles.py    <- creates HR Manager / Viewer groups
|   |   `-- seed_demo_data.py <- loads fictional demo data
|   `-- tests/
|       |-- base.py  test_models.py  test_forms.py
|       |-- test_views.py  test_commands.py
|-- templates/
|   |-- base.html  _messages.html
|   |-- 400.html  403.html  403_csrf.html  404.html  500.html
|   |-- registration/login.html
|   `-- employees/ (dashboard, employee_*, department_*, partials)
`-- static/
    |-- css/style.css
    `-- js/main.js
```

---

## 3. Installation on Windows

### Prerequisites
* **Python 3.10 or newer** (check with `python --version`; install from python.org and tick "Add Python to PATH")
* **MySQL Server 8.x** with MySQL Workbench or the `mysql` command-line client
* **Git**

### Step 1 - Get the project and open a terminal in its folder
```bat
cd path\to\ems_project
```
The folder must contain `manage.py`.

### Step 2 - Create and activate a virtual environment
```bat
python -m venv venv
venv\Scripts\activate
```
Your prompt should now start with `(venv)`.
*PowerShell says "running scripts is disabled"?* Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first, or use the normal Command Prompt (`cmd`).

### Step 3 - Install the dependencies
```bat
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4 - Create the MySQL database and a dedicated user
Open MySQL Workbench (or run `mysql -u root -p`) and execute (choose **your own** strong password):
```sql
CREATE DATABASE ems_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'ems_user'@'localhost' IDENTIFIED BY 'choose-a-strong-password';
GRANT ALL PRIVILEGES ON ems_db.* TO 'ems_user'@'localhost';
GRANT ALL PRIVILEGES ON test_ems_db.* TO 'ems_user'@'localhost';
FLUSH PRIVILEGES;
```
The `test_ems_db` line lets Django create a temporary database when you run the automated tests.

### Step 5 - Configure environment variables
```bat
copy .env.example .env
```
Open `.env` in a text editor and set:
* `DJANGO_SECRET_KEY` - generate one with
  `python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"`
* `DB_NAME`, `DB_USER`, `DB_PASSWORD` - the values from Step 4

`.env` is listed in `.gitignore`, so your password and secret key are never uploaded to GitHub.

### Step 6 - Check the configuration
```bat
python manage.py check
python manage.py makemigrations --check --dry-run
```
Both should finish without errors. If the second command says it detected changes, run `python manage.py makemigrations` and keep the generated file.

### Step 7 - Create the database tables (migrations)
```bat
python manage.py migrate
```

### Step 8 - Create roles, a superuser, and (optionally) demo data
```bat
python manage.py setup_roles
python manage.py createsuperuser
python manage.py seed_demo_data
```
`createsuperuser` asks for a username, e-mail and password (type your own; they are stored hashed in the database). `seed_demo_data` adds 5 fictional departments and 12 fictional employees - handy for demonstrations.

### Step 9 - Run the development server
```bat
python manage.py runserver
```
Open <http://127.0.0.1:8000/> and log in. The Django Admin is at <http://127.0.0.1:8000/admin/>.
Stop the server with `Ctrl + C`. The pages load Bootstrap from a CDN, so an internet connection is needed for the styling.

---

## 4. Run the tests

```bat
python manage.py test
```
Run it with MySQL (needs the `test_ems_db` privilege from Step 4). For a quick run without MySQL you can temporarily use SQLite:
```bat
set DB_ENGINE=sqlite
python manage.py test
```
(PowerShell: `$env:DB_ENGINE="sqlite"`). Useful variants:
```bat
python manage.py test employees.tests.test_forms
python manage.py test employees.tests.test_views.PermissionTests
python manage.py test -v 2
```
The tests cover: models and validators, form validation and normalisation, login/logout, dashboard statistics, search, filters, pagination, employee and department CRUD, delete confirmation, protected department deletion, permissions (viewer / no-permission / anonymous), CSRF rejection, the 404 page, Django Admin pages and the two management commands.

---

## 5. Manual verification checklist

Log in as the superuser and tick each item yourself:

- [ ] Wrong password shows an error; correct password opens the dashboard
- [ ] Logout button (user menu, top right) returns to the login page; the back button does not reopen data pages
- [ ] Dashboard numbers match the employee list; department bars add up
- [ ] Add an employee with valid data -> green success message
- [ ] Try invalid data (bad e-mail, phone `123`, salary `0`, future date, duplicate ID) -> red messages under the fields
- [ ] Open an employee's detail page; edit and save
- [ ] Delete shows a confirmation page; Cancel keeps the record; "Yes, delete" removes it
- [ ] Search by part of a name and by employee ID
- [ ] Filter by department, by status, and by both together; Reset clears them
- [ ] Add, edit and delete a department; deleting one that has employees is blocked with a message
- [ ] Open `/admin/` and manage employees there
- [ ] Create a user in Admin, add them to the **Viewer** group (leave Staff unticked) -> they can see data but have no Add/Edit/Delete buttons, and typing `/employees/add/` gives a 403 page
- [ ] Log out, then open `/employees/` -> redirected to login
- [ ] Open `/employees/99999/` -> friendly 404 page
- [ ] Shrink the browser window (or use developer tools mobile view) -> menu collapses, tables scroll

---

## 6. Common errors and solutions

| Error | Cause and fix |
|-------|---------------|
| `ImproperlyConfigured: Environment variable ... is not set` | `.env` is missing or incomplete. Run `copy .env.example .env` and fill it in. |
| `django.db.utils.OperationalError: (1045, "Access denied for user ...")` | Wrong `DB_USER` / `DB_PASSWORD` in `.env`, or the user was not created (Step 4). |
| `OperationalError: (1049, "Unknown database 'ems_db'")` | Create the database (Step 4) or correct `DB_NAME`. |
| `OperationalError: (2003, "Can't connect to MySQL server")` | MySQL service is not running. Open *Services* in Windows and start **MySQL80**; check `DB_HOST` / `DB_PORT`. |
| `pip install mysqlclient` fails ("Microsoft Visual C++ 14.0 is required", "pkg-config") | Upgrade pip (`python -m pip install --upgrade pip`) so a pre-built wheel is used, or use a Python version for which mysqlclient publishes wheels. Fallback (not part of the delivered configuration): `pip install pymysql` and add `import pymysql; pymysql.install_as_MySQLdb()` at the top of `config/__init__.py`. |
| `ModuleNotFoundError: No module named 'django'` / `'dotenv'` | The virtual environment is not active, or step 3 was skipped. Run `venv\Scripts\activate` then `pip install -r requirements.txt`. |
| Page has no styling | No internet (Bootstrap CDN), or `DJANGO_DEBUG=False` (the development server only serves static files when debug is `True`). |
| `TemplateDoesNotExist` | Run commands from the folder that contains `manage.py`; check template filenames. |
| `Your models have changes that are not yet reflected in a migration` | Run `python manage.py makemigrations` and then `python manage.py migrate`. |
| `CSRF verification failed` | The page was open too long or cookies are blocked. Reload the page and resubmit. |
| `Method Not Allowed (GET): /logout/` | Django 5 logout needs a POST request. Use the Logout button in the user menu. |
| Tests: `Access denied ... to database 'test_ems_db'` | Run the `GRANT ... test_ems_db.*` line from Step 4, or test with `DB_ENGINE=sqlite`. |
| `Error: That port is already in use` | `python manage.py runserver 8001` |
| `UnicodeDecodeError` when reading `.env` | Save `.env` as UTF-8 (without BOM) in your editor. |

---

## 7. Upload to GitHub

1. Make sure secrets are ignored: run `git status` **after** `git init` below and confirm that `.env` and `venv/` do **not** appear in the list.
2. In a terminal inside the project folder:
```bat
git init
git add .
git status
git commit -m "Initial commit: Employee Management System"
```
3. On github.com click **New repository**, name it `employee-management-system`, leave "Add a README" **unticked**, and create it.
4. Connect and push (replace `YOUR-USERNAME`):
```bat
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/employee-management-system.git
git push -u origin main
```
5. Later changes: `git add .`, `git commit -m "describe the change"`, `git push`.

> **If you ever commit `.env` by mistake:** deleting it later is not enough because Git keeps history. Change your MySQL password and generate a new `DJANGO_SECRET_KEY` immediately.

---

## 8. Technology notes

* **Django 5.2 LTS** (MVT pattern), **Python 3.10+**, **MySQL 8** via `mysqlclient`, **python-dotenv** for the `.env` file.
* Bootstrap 5.3 and Bootstrap Icons are loaded from the jsDelivr CDN.
* Class-based views, ModelForms, named URLs, the messages framework, the permission system and the test client are all standard Django features.

## 9. Known limitations

* No account lock-out after repeated failed logins (a package such as `django-axes` could add this).
* No audit log of who changed what.
* Anyone with the *view* permission can see salaries.
* Bootstrap is loaded from a CDN, so the interface needs internet access.
* `0001_initial.py` was written by hand; step 6 (`makemigrations --check`) confirms that it matches the models.

---

## 10. My verification results (fill in yourself)

| Check | Date | Result |
|-------|------|--------|
| `python manage.py check` | | |
| `python manage.py test` (database used: ) | | |
| Manual checklist (section 5) | | |
