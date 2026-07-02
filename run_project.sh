#!/bin/bash

# --- Step 1: Create virtual environment if not exists ---
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# --- Step 2: Activate virtual environment ---
source venv/bin/activate

# --- Step 3: Install dependencies ---
pip install --upgrade pip
pip install -r requirements.txt

# --- Step 3.5: Start PostgreSQL if not already running ---
if ! C:/tmp/pgsql/pgsql/bin/pg_ctl status -D "C:/tmp/postgres_data" >/dev/null 2>&1; then
    echo "Starting PostgreSQL..."
    C:/tmp/pgsql/pgsql/bin/pg_ctl start -D "C:/tmp/postgres_data" -l "C:/tmp/postgres.log" -o "-p 5432"
else
    echo "PostgreSQL is already running."
fi

# --- Step 4: Apply migrations ---
python manage.py makemigrations
python manage.py migrate

# --- Step 5: Run the server ---
python manage.py runserver
