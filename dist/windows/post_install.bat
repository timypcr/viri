@echo off
cd %1
if ""%2""=="""" (
	call virid-conf.bat
) else (
	call virid-conf.bat --host %2
)

python viris.py --startup auto install
python viris.py start
