@echo off
if ""%1""=="""" (
	call virid-conf.bat
) else (
	call virid-conf.bat --host %1
)

python viris.py --startup auto install
python viris.py start
