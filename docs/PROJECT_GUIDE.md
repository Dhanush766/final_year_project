# Employee Management System - Project Guide

This guide helps you **understand, present and defend** the project. Installation and run steps are in `README.md`.

**Honest status note:** the code was written and statically checked (syntax, URL names, template references, imports), but the automated tests and the running application have **not** been executed by the generator. Run them yourself and record the results (README section 10) before presenting. Never tell an examiner that something "was tested" unless you ran it.

---

## 1. Project overview

The Employee Management System (EMS) is a web application that lets an organisation's administrators and HR staff keep employee records in one place instead of paper files or scattered spreadsheets. Authorised users can log in, see a dashboard with headcount statistics, add, view, update and delete employees, search and filter them, and manage departments. It is built with Django (Python), MySQL, and Django templates styled with Bootstrap 5.

**One-sentence pitch:** *"A secure, responsive Django web app with MySQL that digitises employee record management, with role-based access, validation and a statistics dashboard."*

---

## 2. Problem statement and objectives

### Problem statement
Small and medium organisations often store employee information in spreadsheets or paper registers. This causes duplicate or inconsistent records, slow searching, no control over who can change data, and no quick view of workforce statistics. A simple, secure, web-based system is needed.

### Objectives
1. Store employee and department data centrally in a relational database (MySQL).
2. Provide secure login so only authorised people can view or change data.
3. Allow create, read, update and delete (CRUD) operations on employees and departments.
4. Make finding records fast through search and filters.
5. Prevent bad data through server-side validation (unique IDs, valid e-mail, phone, salary, dates).
6. Give managers a dashboard summarising the workforce.
7. Provide a responsive interface usable on desktop and mobile.
8. Include automated tests so the application can be changed safely.

### Scope
**In scope:** the features above. **Out of scope (future work):** payroll, attendance, leave workflows, employee self-service login, file uploads, e-mail notifications.

---

## 3. System architecture

### 3.1 The MVT pattern (Django's version of MVC)

```
 Browser (HTML + Bootstrap + JS)
        |  HTTP request
        v
 +--------------------------- Django ---------------------------+
 |  config/urls.py  -->  employees/urls.py   (URL routing)       |
 |        |                                                      |
 |        v                                                      |
 |  Middleware: Security, Session, CSRF, Auth, Messages          |
 |        |                                                      |
 |        v                                                      |
 |  employees/views.py   (VIEW: logic + permission checks)       |
 |     |        |                                                |
 |     |        +--> employees/forms.py (validation)             |
 |     v                                                         |
 |  employees/models.py  (MODEL: tables via the ORM) <----+      |
 |     |                                                  |      |
 |     v                                                  |      |
 |  MySQL database                                        |      |
 |                                                        |      |
 |  templates/*.html (TEMPLATE: builds the HTML page) ----+      |
 +---------------------------------------------------------------+
        |  HTTP response (HTML)
        v
     Browser
```

| Layer | Django part | Our files |
|-------|-------------|-----------|
| Model | Describes data and talks to MySQL through the ORM | `models.py`, `validators.py`, `migrations/` |
| View | Receives a request, checks permissions, uses models/forms, returns a response | `views.py`, `urls.py` |
| Template | HTML with placeholders | `templates/`, `static/` |
| Forms | Validate and clean user input | `forms.py` |

### 3.2 Request flow example - "Add employee"
1. User opens `/employees/add/`. `urls.py` maps it to `EmployeeCreateView`.
2. Middleware loads the session and user. `SecureViewMixin` checks: logged in? has `employees.add_employee`? If not logged in -> redirect to login; logged in without permission -> 403 page.
3. For a GET request the view shows an empty `EmployeeForm` using `employee_form.html`.
4. For a POST request the CSRF middleware verifies the token, then `EmployeeForm` validates every field and checks uniqueness in the database.
5. Valid -> the ORM saves a row in MySQL, a success message is stored, and the user is redirected to the list (Post/Redirect/Get). Invalid -> the form is shown again with error messages.

### 3.3 Security layers
| Threat | Protection used |
|--------|-----------------|
| Anonymous access | `LoginRequiredMixin` on every page |
| Unauthorised changes | `PermissionRequiredMixin` with Django permissions; 403 page |
| Cross-site request forgery | Django CSRF middleware + `{% csrf_token %}` in every form |
| SQL injection | Django ORM uses parameterised queries (no raw SQL) |
| Cross-site scripting (XSS) | Template auto-escaping |
| Password theft from the database | Passwords stored hashed by Django (PBKDF2 by default) |
| Secrets in source code | Secret key and DB credentials come from environment variables / `.env` (ignored by Git) |
| Bad data | Validators and form `clean_` methods run on the server |
| Logout via link (CSRF-style logout) | Logout only accepts POST |
| Clickjacking | `XFrameOptionsMiddleware` |

---

## 4. Complete folder structure and file reference

See README section 2 for the tree. Every file, its purpose and what it depends on:

| File | Purpose | Depends on |
|------|---------|------------|
| `manage.py` | Command-line entry point (`runserver`, `migrate`, `test`, ...) | `config.settings` |
| `config/settings.py` | All configuration; reads `.env` | `python-dotenv`, environment variables |
| `config/urls.py` | Root routes: `/admin/`, `/login/`, `/logout/`, include app URLs | `employees.views`, `employees.urls` |
| `config/wsgi.py`, `asgi.py` | Entry points for production servers | settings |
| `employees/models.py` | `Department` and `Employee` tables | `validators.py` |
| `employees/validators.py` | Reusable checks: ID format, name, phone, salary > 0, date not in future | Django only |
| `employees/migrations/0001_initial.py` | Creates the two tables and an index | `models.py`, `validators.py` |
| `employees/forms.py` | `EmployeeForm`, `DepartmentForm`, `EmployeeFilterForm`, login form, Bootstrap styling mixin | `models.py` |
| `employees/views.py` | All pages and permission rules | `forms.py`, `models.py` |
| `employees/urls.py` | Named URL patterns in namespace `employees` | `views.py` |
| `employees/admin.py` | Django Admin screens for both models | `models.py` |
| `employees/context_processors.py` | Gives templates `SITE_NAME` and `CURRENCY_SYMBOL` | settings |
| `employees/management/commands/setup_roles.py` | Creates "HR Manager" and "Viewer" groups | Django auth |
| `employees/management/commands/seed_demo_data.py` | Loads fictional demo data | `models.py` |
| `employees/tests/*.py` | Automated tests | everything above |
| `templates/base.html` | Page layout: navbar, messages, footer | Bootstrap CDN, `static/` |
| `templates/registration/login.html` | Login page | `base.html`, login form |
| `templates/employees/*.html` | Dashboard, lists, details, forms, delete confirmations | `base.html`, views' context |
| `templates/40x/500.html` | Friendly error pages | `base.html` (500/400/csrf are standalone) |
| `static/css/style.css`, `static/js/main.js` | Small style and behaviour improvements | `base.html` |
| `requirements.txt` | Python packages | - |
| `.env.example`, `.gitignore` | Config template; files Git must ignore | - |

### URL table
| URL name | Path | View | Permission |
|----------|------|------|------------|
| `login` / `logout` | `/login/`, `/logout/` | `AppLoginView`, `AppLogoutView` | - |
| `employees:dashboard` | `/` | `DashboardView` | view_employee |
| `employees:employee_list` | `/employees/` | `EmployeeListView` | view_employee |
| `employees:employee_add` | `/employees/add/` | `EmployeeCreateView` | add_employee |
| `employees:employee_detail` | `/employees/<pk>/` | `EmployeeDetailView` | view_employee |
| `employees:employee_edit` | `/employees/<pk>/edit/` | `EmployeeUpdateView` | change_employee |
| `employees:employee_delete` | `/employees/<pk>/delete/` | `EmployeeDeleteView` | delete_employee |
| `employees:department_list` | `/departments/` | `DepartmentListView` | view_department |
| `employees:department_add` | `/departments/add/` | `DepartmentCreateView` | add_department |
| `employees:department_edit` | `/departments/<pk>/edit/` | `DepartmentUpdateView` | change_department |
| `employees:department_delete` | `/departments/<pk>/delete/` | `DepartmentDeleteView` | delete_department |

---

## 5. Database design

### 5.1 Tables

**employees_department**
| Column | Type | Rules |
|--------|------|-------|
| id | BIGINT | Primary key, auto-increment |
| name | VARCHAR(100) | Required, **unique** |
| description | TEXT | Optional |
| created_at | DATETIME | Set automatically on creation |

**employees_employee**
| Column | Type | Rules |
|--------|------|-------|
| id | BIGINT | Primary key, auto-increment |
| employee_id | VARCHAR(20) | Required, **unique**, letters/digits/hyphens, stored upper-case |
| full_name | VARCHAR(150) | Required, letters, spaces, `.` `'` `-`, min 2 characters |
| email | VARCHAR(254) | Required, **unique**, valid format, stored lower-case |
| phone_number | VARCHAR(16) | Required, 10-15 digits, optional leading `+` |
| department_id | BIGINT | **Foreign key** -> department.id, `ON DELETE PROTECT` |
| designation | VARCHAR(100) | Required |
| salary | DECIMAL(10,2) | Required, greater than 0 |
| joining_date | DATE | Required, not in the future |
| status | VARCHAR(12) | One of ACTIVE, ON_LEAVE, RESIGNED, TERMINATED; default ACTIVE |
| created_at / updated_at | DATETIME | Automatic timestamps |

Index: `emp_status_idx` on `status` (speeds up dashboard counts and status filters). Unique constraints also create indexes on `employee_id` and `email`. Users come from Django's built-in `auth_user` table (not shown).

### 5.2 ER diagram (text)

```
 +-------------------+ 1                    N +----------------------+
 |    DEPARTMENT     |------------------------|       EMPLOYEE       |
 +-------------------+  "has many employees"  +----------------------+
 | PK id             |                        | PK id                |
 |    name (unique)  |                        |    employee_id (UQ)  |
 |    description    |                        |    full_name         |
 |    created_at     |                        |    email (UQ)        |
 +-------------------+                        |    phone_number      |
                                              | FK department_id     |
                                              |    designation       |
                                              |    salary            |
                                              |    joining_date      |
                                              |    status            |
                                              |    created_at        |
                                              |    updated_at        |
                                              +----------------------+
```
**Relationship:** one department has many employees; each employee belongs to exactly one department (one-to-many). Because the foreign key uses `PROTECT`, MySQL/Django will not allow deleting a department that still has employees - this prevents orphaned records.

**Normalisation:** department data is stored once and referenced by key (3NF), so renaming a department updates it for every employee.

---

## 6. Implementation plan (how the project was built, in stages)

| Stage | What | Files | How to check it |
|-------|------|-------|-----------------|
| 1 | Project skeleton, environment-based settings, MySQL config | `manage.py`, `config/`, `.env.example`, `requirements.txt`, `.gitignore` | `python manage.py check` |
| 2 | Data layer | `models.py`, `validators.py`, `migrations/` | `python manage.py migrate`, then look at the tables in MySQL Workbench |
| 3 | Admin integration | `admin.py` | `createsuperuser`, open `/admin/` |
| 4 | Forms and validation | `forms.py` | `python manage.py test employees.tests.test_forms` |
| 5 | Views, URLs, permissions | `views.py`, `urls.py` | `python manage.py test employees.tests.test_views` |
| 6 | Templates and static files | `templates/`, `static/` | `runserver`, click through every page |
| 7 | Roles and demo data | `management/commands/` | `setup_roles`, `seed_demo_data` |
| 8 | Tests and documentation | `tests/`, `README.md`, this guide | `python manage.py test` |

---

## 7. Requirement-to-implementation map

| # | Requirement | Implementation | Automated test that targets it (not yet run by you) |
|---|-------------|----------------|-----------------------------------------------------|
| 1 | Login/logout | `AppLoginView`, `AppLogoutView` | `AuthenticationTests` |
| 2 | Dashboard | `DashboardView` | `DashboardTests` |
| 3 | Add employee | `EmployeeCreateView` | `EmployeeCrudTests.test_add_*` |
| 4 | View all | `EmployeeListView` | `EmployeeListTests` |
| 5 | View details | `EmployeeDetailView` | `test_detail_page` |
| 6 | Update | `EmployeeUpdateView` | `test_edit_employee` |
| 7 | Delete with confirmation | `EmployeeDeleteView` + confirm template | `test_delete_*` |
| 8 | Search | `Q(full_name__icontains) \| Q(employee_id__icontains)` | `test_search_*` |
| 9 | Filter | `EmployeeFilterForm` | `test_filter_*`, `test_combined_filters` |
| 10 | Departments | Department views/templates | `DepartmentCrudTests` |
| 11 | Validation | `validators.py`, `forms.py`, model constraints | `test_forms.py`, `test_models.py` |
| 12 | Messages | Django messages + `FormFeedbackMixin` | message assertions in view tests |
| 13 | Responsive UI | Bootstrap grid, collapsible navbar, `table-responsive` | manual (resize browser) |
| 14 | MySQL | `DATABASES` in settings | manual (`migrate`, inspect tables) |
| 15 | Django Admin | `admin.py` | `AdminIntegrationTests` |
| 16 | Tests | `employees/tests/` | - |
| 17 | Access control | `SecureViewMixin`, groups, CSRF | `PermissionTests` |
| 18 | Error handling | 400/403/404/500 templates, `ProtectedError` handling, safe filter handling | `test_detail_of_missing_employee_is_404`, `test_department_with_employees_cannot_be_deleted`, `test_invalid_filter_values_do_not_crash` |

Requirement 13 and 14 can only be confirmed manually.

---

## 8. Testing procedure

### 8.1 Automated tests
```bat
python manage.py test
```
Expected result when everything passes: a line such as `Ran NN tests in X.XXXs` followed by `OK`. If a test fails, read the traceback bottom-up: the last lines show which assertion failed and why. **Send me the full output and I will help you fix it.**

### 8.2 Manual testing
Use the checklist in README section 5. For each failed item write down: page URL, what you did, what you expected, what happened.

### 8.3 Good practice when presenting
* State clearly: "The project includes N automated tests; I ran them on <date> and <result>."
* Do not claim browser or device compatibility beyond what you actually tried.

---

## 9. Final-year project abstract

> **Employee Management System - A Web-Based Application for Managing Employee Records**
>
> Managing employee information manually through paper registers or spreadsheets leads to duplicated data, slow retrieval, errors and weak access control. This project presents a web-based Employee Management System developed with the Python Django framework, MySQL relational database and a responsive Bootstrap interface rendered through Django templates. The system follows the Model-View-Template architecture and provides secure authentication, role-based permissions, and complete create, read, update and delete operations for employees and departments. Employee records contain the employee ID, name, e-mail, phone number, department, designation, salary, joining date and employment status. Server-side validation enforces unique identifiers, valid contact details, positive salaries and realistic joining dates, while a dashboard summarises total and active employees and department-wise distribution. Users can search by name or employee ID and filter by department and employment status. Security features include CSRF protection, password hashing, permission checks on every view, protected deletion of departments that still have employees, and storage of secrets in environment variables. The Django Admin site is integrated for back-office management, and an automated test-suite supports maintainability. The system demonstrates how a standard full-stack Python toolchain can deliver a secure, maintainable and user-friendly solution to a common organisational need.
>
> **Keywords:** Django, Python, MySQL, Bootstrap, employee management, role-based access control, CRUD, web application.

---

## 10. Project report outline

1. **Title page, certificate, declaration, acknowledgement**
2. **Abstract** (section 9)
3. **Table of contents, list of figures, list of tables**
4. **Chapter 1 - Introduction:** background, problem statement, objectives, scope, organisation of the report
5. **Chapter 2 - Literature / existing system survey:** manual systems, spreadsheets, commercial HRMS tools; limitations; proposed system; why Django and MySQL
6. **Chapter 3 - System analysis:** feasibility (technical, economic, operational), functional requirements (the 18 features), non-functional requirements (security, usability, performance, maintainability), hardware/software requirements, user roles
7. **Chapter 4 - System design:** architecture (MVT diagram), use-case diagram, data-flow diagrams (level 0 and 1), ER diagram, table structures, class/model diagram, UI wireframes, security design
8. **Chapter 5 - Implementation:** development environment, project structure, key modules (models, forms/validation, views/permissions, templates), code snippets with explanation, challenges and solutions
9. **Chapter 6 - Testing:** test strategy, unit and integration tests, test cases table (ID, description, input, expected, actual, status), manual test results, screenshots. *Fill "actual" and "status" only from tests you ran.*
10. **Chapter 7 - Results and screenshots:** login, dashboard, list, forms with validation errors, detail, delete confirmation, departments, admin, mobile view
11. **Chapter 8 - Conclusion and future scope:** achievements, limitations, enhancements (leave management, attendance, payroll, REST API, e-mail alerts, audit trail, account lock-out, CSV/PDF export)
12. **References** (Django documentation, MySQL documentation, Bootstrap documentation, Python documentation)
13. **Appendices:** installation guide, source-code listing, sample data

---

## 11. Demonstration script (about 10-12 minutes)

**Before you start (checklist):** MySQL service running; virtual environment active; `python manage.py runserver` running; demo data loaded with `seed_demo_data`; a Viewer user created; two browser windows ready (one logged in as admin, one as viewer); internet on (Bootstrap CDN).

| Time | What you do | What you say |
|------|-------------|--------------|
| 0:00 | Show the login page | "This is the Employee Management System built with Django, MySQL and Bootstrap. Every page requires login." |
| 0:45 | Enter a wrong password, then the correct one | "Authentication uses Django's built-in system; passwords are stored hashed." |
| 1:30 | Dashboard | "The dashboard shows total and active employees, department statistics and recent additions. These come from database aggregation queries using the ORM." |
| 3:00 | Employee list: search "Aarav", then search "EMP007" | "Search works on name and employee ID using case-insensitive matching." |
| 4:00 | Filter by department, by status, combined, then Reset | "Filters are validated by a Django form, so invalid values cannot break the query." |
| 5:00 | Add an employee: first submit with errors (bad e-mail, phone `123`, duplicate ID), then correct data | "Validation happens on the server, so it cannot be bypassed from the browser. The form also normalises data: ID to upper-case, e-mail to lower-case." |
| 6:30 | Open detail page, edit, save | "Update uses the same form. Uniqueness checks exclude the record being edited." |
| 7:30 | Delete: show confirmation, cancel, then confirm | "Deletion needs a POST after a confirmation page, so a stray link cannot delete data." |
| 8:15 | Departments: add one; try to delete one that has employees | "The foreign key is PROTECT, so a department with employees cannot be deleted. The app shows a clear message instead of crashing." |
| 9:00 | Switch to the viewer window | "This user is in the Viewer group: they can see data but there are no Add/Edit/Delete buttons. If they type the URL directly they get a 403 page." |
| 10:00 | Open `/admin/` | "Django Admin is integrated for back-office tasks, with search, filters and date drill-down." |
| 10:30 | Resize the window | "The layout is responsive - menu collapses and tables scroll on small screens." |
| 11:00 | Show test results and the `.env` / `.gitignore` | "I ran the automated tests on <date> with this result: <your real result>. Secrets live in `.env` which Git ignores." |

**Tips:** rehearse twice; keep the VS Code project tree ready to show `models.py` and `views.py`; do not demo a feature you have not rehearsed; if something fails live, stay calm and say what you would check (terminal log, form errors, database).

---

## 12. Interview questions and answers

**Project basics**

1. **What is your project about?** A web application to manage employee records - add, view, update, delete, search and filter employees, manage departments, and see statistics - with secure login and role-based permissions.
2. **Why did you choose Django?** It includes authentication, ORM, forms, admin, templates and security protections out of the box, so I could build a secure application quickly and keep the code organised.
3. **Explain the MVT architecture.** Model = data and database access; View = logic that receives a request and returns a response; Template = HTML presentation. The URL configuration routes requests to views.
4. **How is MVT different from MVC?** Django's *view* plays the role of an MVC controller, and Django's *template* plays the role of the MVC view; the framework itself acts as the controller that routes requests.
5. **Why MySQL?** It is a widely used, reliable relational database that supports constraints, indexes and transactions. Django supports it through `mysqlclient`.

**Django concepts**

6. **What are migrations?** Python files describing database schema changes. `makemigrations` creates them from model changes; `migrate` applies them to the database.
7. **What is the ORM and why use it?** It lets me query the database with Python instead of SQL. It also protects against SQL injection by using parameterised queries.
8. **What is a ModelForm?** A form generated from a model. It validates input, uses the model's rules (including uniqueness) and can save directly to the database.
9. **Why class-based views?** They reduce repetition for common tasks (list, detail, create, update, delete) and let me reuse behaviour with mixins, such as my permission mixin.
10. **What is a Django mixin?** A small class providing reusable behaviour. `SecureViewMixin` combines login and permission checks; `FormFeedbackMixin` adds success/error messages.
11. **What are named URLs and why use them?** Each route has a name, so templates use `{% url 'employees:employee_list' %}` instead of hard-coded paths. If the path changes, nothing else needs editing.
12. **What is the messages framework?** It stores one-time messages (success, error) in the session so they survive a redirect and are shown once.
13. **What does `select_related` do?** It joins the related table in one query so listing 10 employees with their departments does not run 11 queries (it avoids the N+1 problem).
14. **How do you build the dashboard statistics?** With ORM aggregation: `Count` with `filter=Q(...)` per department, and `.count()` for totals.

**Security**

15. **How is access controlled?** `LoginRequiredMixin` forces login; `PermissionRequiredMixin` checks Django permissions for each action. Anonymous users go to login; logged-in users without permission get a 403 page. Templates also hide buttons the user may not use, but the real protection is in the views.
16. **What is CSRF and how do you prevent it?** An attack where another site makes your browser submit a request while you are logged in. Django's CSRF middleware requires a secret token in every POST form (`{% csrf_token %}`).
17. **How do you protect passwords and secrets?** Django hashes passwords (PBKDF2). The secret key and database credentials are read from environment variables in `.env`, which `.gitignore` excludes.
18. **How do you prevent XSS?** Django templates automatically escape output, so injected `<script>` text is shown as text.
19. **Why does logout use POST?** A GET logout could be triggered by an image or link on another site. Django 5 therefore requires POST.
20. **What security features are missing?** Account lock-out after repeated failed logins, audit logging, two-factor authentication, and field-level restriction of salary visibility. These are listed as future work.

**Design decisions**

21. **Why `on_delete=PROTECT` for the department foreign key?** To stop accidental deletion of a department that still has employees, which would either orphan or silently delete data. The view catches the error and shows a friendly message.
22. **Why do you validate on the server when the browser already validates?** Browser checks can be bypassed (developer tools, scripts). Server validation is the real guarantee; browser checks are only convenience.
23. **How do you ensure employee IDs and e-mails are unique?** Database `UNIQUE` constraints plus form validation that shows a friendly error. Values are normalised (upper-case ID, lower-case e-mail) so `emp1` and `EMP1` cannot both exist.
24. **How does search work?** `Q(full_name__icontains=q) | Q(employee_id__icontains=q)` - a case-insensitive "contains" match on either field. Filters add `.filter(department=...)` and `.filter(status=...)`.
25. **How does pagination work?** `paginate_by = 10` on the ListView; the template keeps the current search/filter values in the page links.
26. **Why store salary as DecimalField?** Floats give rounding errors for money; Decimal is exact.

**Testing and process**

27. **How did you test the project?** I wrote unit and integration tests with Django's test framework covering models, validation, views, permissions and the admin. *(Say what you really ran: "I ran them on <date> and <result>".)*
28. **What does `TestCase` do?** It creates a temporary test database and wraps each test in a transaction that is rolled back, so tests do not affect real data.
29. **What would you improve next?** REST API with Django REST Framework, leave and attendance modules, CSV/PDF export, audit log, account lock-out, and deployment with Gunicorn + Nginx.
30. **What was the biggest challenge?** *(Give your honest answer; for example: configuring MySQL on Windows, understanding permissions, or debugging validation errors.)*

**Be ready to show the code for:** `models.py` (Employee), `EmployeeListView.get_queryset`, `SecureViewMixin`, and one test.

---

## 13. Limitations and future enhancements

**Current limitations**
* No lock-out after repeated failed logins; no audit trail; salary visible to every user with the view permission.
* Bootstrap loads from a CDN (needs internet).
* Employee status has four fixed values; there is no leave or attendance tracking.
* `0001_initial.py` was hand-written; confirm with `python manage.py makemigrations --check --dry-run`.
* Not yet executed or load-tested by the generator.

**Possible enhancements:** REST API, CSV/Excel/PDF export, profile photos, e-mail notifications, audit log, two-factor authentication, charts on the dashboard, Docker deployment, CI pipeline running the tests on every push.
