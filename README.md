# Teaching Internet Basics — NetWise
A Flask and MySQL learning portal for teaching safe, effective everyday Internet use. Students work through database-backed lessons, tracked progress, scored quizzes, feedback and surveys; administrators manage learning content and review operational data.

## Stack
Python 3, Flask, SQLAlchemy, Flask-Migrate, Flask-Login, Flask-WTF, MySQL (production), SQLite (local testing), Bootstrap 5 and Jinja2.

## Setup
1. `python -m venv .venv && source .venv/bin/activate`
2. `pip install -r requirements.txt`
3. `cp .env.example .env` and set a strong `SECRET_KEY` and MySQL `DATABASE_URL`.
4. Create the MySQL database named in the URL. For local SQLite, use `DATABASE_URL=sqlite:///instance/portal.db`.
5. `flask --app run.py db init` (once), then `flask --app run.py db migrate -m "initial schema" && flask --app run.py db upgrade`.
6. `python seed/seed.py`, then `flask --app run.py run`.

## Development accounts
Seeded accounts are **development-only**: `admin@netwise.local` / `ChangeMe123!` and `student@netwise.local` / `Student123!`. Replace or remove these before deployment.

## Tests
Run `pytest`. Tests use isolated SQLite data and CSRF is enabled in production/development.

## Security
Secrets stay in environment variables. Passwords use Werkzeug hashes; protected routes enforce roles server-side; CSRF, ORM parameterisation, secure cookie settings and baseline security headers are enabled.

## Screenshots
Capture deployment screenshots here for the academic report.

## Future enhancements
Email notifications, granular admin audit logs, content image uploads with validation, and server-generated PDF certificates.
