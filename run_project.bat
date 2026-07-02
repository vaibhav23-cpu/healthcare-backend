@echo off
REM --- Step 1: Create virtual environment if not exists ---
IF NOT EXIST venv (
    python -m venv venv
)

REM --- Step 2: Activate virtual environment ---
call venv\Scripts\activate

REM --- Step 3: Install dependencies ---
pip install --upgrade pip
pip install -r requirements.txt

REM --- Step 3.5: Start PostgreSQL if not already running ---
C:\tmp\pgsql\pgsql\bin\pg_ctl.exe status -D "C:\tmp\postgres_data" >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Starting PostgreSQL...
    C:\tmp\pgsql\pgsql\bin\pg_ctl.exe start -D "C:\tmp\postgres_data" -l "C:\tmp\postgres.log" -o "-p 5432"
) ELSE (
    echo PostgreSQL is already running.
)

REM --- Step 4: Apply migrations ---
python manage.py makemigrations
python manage.py migrate

REM --- Step 5: Run the server ---
python manage.py runserver

pause
