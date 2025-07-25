@echo off

set PYTHON_EXE=python3.12

%PYTHON_EXE% --version || (
    echo Required Python version not found: %PYTHON_EXE%
    exit /b 1
)

%PYTHON_EXE% -m venv ./venv

call ./venv/Scripts/activate

python -m pip install --upgrade pip
if exist requirements.txt (
    pip install -r requirements.txt
)

echo Setup complete.