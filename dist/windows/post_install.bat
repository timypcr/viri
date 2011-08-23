@echo off
call virid-conf.bat
python viris.py --startup auto install
python viris.py start
