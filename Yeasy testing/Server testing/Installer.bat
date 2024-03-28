@echo off
REM REM Step 1: Create virtual environment
REM python -m venv venv
REM echo Step 1 completed
REM pause

REM REM Step 2: Activate the virtual environment
REM .\venv\Scripts\activate.bat
REM echo Step 2 completed
REM pause

REM Step 3: Install requirements
pip install -r requirements.txt
echo Step 3 completed
pause

REM Step 4: Run Flask application
python -m flask --app api run --debug
echo Step 4 completed
pause

REM Step 5: Wait 
pause 