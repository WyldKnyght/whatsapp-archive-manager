@echo off
REM First time: py -m venv .venv && .venv\Scripts\pip install -r requirements.txt
if exist .venv\Scripts\python.exe (set PY=.venv\Scripts\python.exe) else (set PY=py)
%PY% -m wa_archive serve
