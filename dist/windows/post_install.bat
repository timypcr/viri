@echo off
call virid-conf.bat
python viris.py install
python viris.py start
