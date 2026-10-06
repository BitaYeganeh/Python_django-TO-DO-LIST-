# Django To-Do App 📝

[![Tests](https://github.com/BitaYeganeh/Python_django-TO-DO-LIST-/actions/workflows/tests.yml/badge.svg)](https://github.com/BitaYeganeh/Python_django-TO-DO-LIST-/actions/workflows/tests.yml)

A simple and interactive **To-Do List web application** built with Django. Users can sign up, log in, add tasks, mark them as complete, and delete them. A **public demo mode** allows visitors to try the app without creating an account.

---

## Features

- **User Authentication**: Sign up, log in, and log out securely.
- **Task Management**:
  - Add tasks
  - Mark tasks as complete / undo
  - Delete tasks
- **User-Specific Tasks**: Each user sees only their own tasks.
- **Demo Mode**: Public demo tasks viewable without signing up.
- **Responsive UI**: Styled with CSS for a clean interface.

---

## Demo

- Visit the [Demo Page](http://127.0.0.1:8000/demo/) to try the app without an account.
- Sign up to create and manage your own tasks.

---

## Testing

22 automated tests (Django `TestCase`) run on every push with GitHub Actions.

| Area | What is checked |
| --- | --- |
| Model | Defaults, `__str__`, tasks removed with their user |
| Form | Title is required and limited to 200 characters |
| Sign-up | Creates and logs in the user; mismatched passwords are rejected |
| Tasks | Add, complete (toggle) and delete; empty titles are not saved |
| Security | Users only see and change their own tasks (others get 404); the demo account and visitors cannot edit |
| Demo mode | Visitors see demo tasks; the site still works when no demo user exists |

### Run it locally

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd todo_project
python manage.py migrate
python manage.py test tasks
python manage.py runserver
```
