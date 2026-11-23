# Guess The Nation

A country-guessing game built with a Flask server and a SQLite database. Users register and log in, and each correct guess is saved to their own account so they can track their progress.

## Resources

### User
| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | integer | Unique id, assigned automatically |
| `first_name` | text | The user's first name |
| `last_name` | text | The user's last name |
| `email` | text | The user's email. Must be unique (case-insensitive) and is used to log in |
| `password_hash` | text | The bcrypt hash of the user's password. Never returned by the API |

### Country (saved correct guess)
| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | integer | Unique id, assigned automatically |
| `common_name` | text | The commonly used name of the country |
| `official_name` | text | The country's official name |
| `population` | integer | The country's population |
| `html_flag_code` | text | HTML entity code for the country's flag |
| `area` | integer | Land area in square miles |
| `user_id` | integer | The id of the user who made the guess. Set by the server from the session |

## Database Schema

```sql
-- users table
CREATE TABLE users(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE COLLATE NOCASE,
  password_hash TEXT NOT NULL
);

-- countries table
CREATE TABLE countries(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  common_name TEXT NOT NULL,
  official_name TEXT NOT NULL,
  population INTEGER NOT NULL,
  html_flag_code TEXT NOT NULL,
  area INTEGER NOT NULL,
  user_id INTEGER
);
```

Each country row belongs to the user whose id is in its `user_id` column.

## REST API Endpoints

| Name | Method | Path | Auth required? | Success | Errors |
|------|--------|------|----------------|---------|--------|
| Create user (register) | `POST` | `/users` | No | 201 | 400, 409 (email already registered) |
| Create session (log in) | `POST` | `/sessions` | No | 200 | 400, 401 |
| Get current session | `GET` | `/sessions/current` | No | 200 | 401 |
| Delete session (log out) | `DELETE` | `/sessions` | No | 200 | none |
| List countries | `GET` | `/countries` | Yes | 200 | 401 |
| Retrieve country | `GET` | `/countries/<id>` | Yes | 200 | 401, 404 |
| Create country | `POST` | `/countries` | Yes | 201 | 400, 401 |
| Replace country | `PUT` | `/countries/<id>` | Yes | 200 | 400, 401, 404 |
| Delete country | `DELETE` | `/countries/<id>` | Yes | 200 | 401, 404 |
| Look up country info (proxy to restcountries.com) | `GET` | `/api/country/<name>` | Yes | 200 | 401, 404, 502 |

## Authentication and Sessions

- **Session store:** an in-memory dictionary on the server that maps a random session id to `{"user_id": <id>}`. Nothing else is stored. It is cleared when the server restarts.
- **Cookie:** `session_id`, set on login with `HttpOnly` and `SameSite=Lax`. It is cleared on logout.
- **Restricted resource:** countries. Every `/countries` route returns `401` without a valid session, and a user only sees their own rows. Another user's row returns `404`.

## Password Hashing

- **Method:** bcrypt, using Flask-Bcrypt.
- **Parameters:** cost factor 12 (the default), with a unique random salt per password. The result is one 60-character string (`$2b$12$...`) that contains the salt.
- **Limits:** passwords must be 8 to 72 characters, because bcrypt only uses the first 72 bytes.
- **Plain-text handling:** the plain-text password is only used in memory to create or check the hash. It is never stored or returned.

## Running the Project

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # I've loaded the example env with a live key
python app.py
```

Then open <http://localhost:5500>.

## Configuration

The restcountries.com API key is read from the `RESTCOUNTRIES_KEY` environment variable (loaded from a git-ignored `.env` file). It is only used on the server: the browser calls `/api/country/<name>`, and the server adds the key, caches each answer in memory, and returns the JSON. The page needs a logged-in session to use it.

`tools/build_country_lists.py` (a one-off script that rebuilds the country-name lists in `static/data/countries/`) reads the same variable.

