@echo off

: 
: Simple batch script for building a Viri installer on Windows
: Copyright 2011, Jesús Corrius <jcorrius@gmail.com>
: Version 0.1  03/08/2011
:

rem ---------------------------------------------------------------------------
rem --              set the appropiate values for your system                --
rem ---------------------------------------------------------------------------

set output_directory=build
set full_path_to_python_exe=c:\dev\Python-3.2.1\PCbuild\python.exe
set full_path_to_cxfreeze=c:\dev\Python-3.2.1\Scripts\cxfreeze
set full_path_to_viric=c:\dev\viri\client\viric
set full_path_to_virid=c:\dev\viri\virid\bin\virid
set full_path_to_virid_includes=c:\dev\viri\virid;c:\dev\viri\virid\viri
set full_path_to_virid_conf=c:\dev\viri\virid\bin\virid-conf
set full_path_to_upx_exe=c:\dev\upx307w\upx.exe
set full_path_to_c_runtime="c:\Program Files\Microsoft Visual Studio 9.0\VC\redist\x86\Microsoft.VC90.CRT\msvcr90.dll"
set full_path_to_c_redist=c:\dev\vcredist\vcredist_x86.exe
set full_path_to_wix_bin="c:\Program Files\Windows Installer XML v3.5\bin"
set full_path_to_wix_script=C:\dev\wix\viri.wxs


rem ---------------------------------------------------------------------------

echo *** Step 1. Sanity check of your environment...
echo.
if exist %full_path_to_python_exe% (
	echo * Python found at: %full_path_to_python_exe%
) else (
	echo * Python not found!
	goto :eof
)
if exist %full_path_to_cxfreeze% (
	echo * cxfreeze found at: %full_path_to_cxfreeze%
) else (
	echo * cxfreeze not found!
	goto :eof
)
if exist %full_path_to_viric% (
	echo * viric found at: %full_path_to_viric%
) else (
	echo * viric not found!
	goto :eof
)
if exist %full_path_to_virid% (
	echo * virid found at: %full_path_to_virid%
) else (
	echo * virid not found!
	goto :eof
)
if exist %full_path_to_virid_conf% (
	echo * virid-conf found at: %full_path_to_virid_conf%
) else (
	echo * virid-conf not found!
	goto :eof
)
if exist %full_path_to_upx_exe% (
	echo * UPX found at: %full_path_to_upx_exe%
) else (
	echo * UPX not found!
	goto :eof
)
if exist %full_path_to_c_runtime% (
	echo * C runtime found at: %full_path_to_c_runtime%
) else (
	echo * C runtime not found!
	goto :eof
)
if exist %full_path_to_c_redist% (
	echo * C runtime redistributables found at: %full_path_to_c_redist%
) else (
	echo * C runtime redistributables not found!
	goto :eof
)
if exist %full_path_to_wix_bin%\candle.exe (
	echo * WIX toolchain found at: %full_path_to_wix_bin%
) else (
	echo * WIX toolchain not found!
	goto :eof
)
if exist %full_path_to_wix_script% (
	echo * WIX script found at: %full_path_to_wix_script%
) else (
	echo * WIX script not found!
	goto :eof
)
echo * Output directory: %output_directory%
echo.

echo *** Step 2. Deleting previous generated files (if exist)...
echo.
if exist %output_directory% (
	rmdir /s /q build rem 2>nul
)
echo * Done.
echo.

echo *** Step 3. Freezing viric...
echo.
%full_path_to_python_exe% %full_path_to_cxfreeze% %full_path_to_viric% --target-dir %output_directory% -OO -c -s

echo.

echo *** Step 4. Freezing virid...
echo.
%full_path_to_python_exe% %full_path_to_cxfreeze% %full_path_to_virid% --target-dir %output_directory% -OO -c -s --include-path %full_path_to_virid_includes% --include-modules objects,orm,rpcserver

echo.

echo *** Step 5. Freezing virid.conf...
echo.
rem %full_path_to_python_exe% %full_path_to_cxfreeze% %full_path_to_virid_conf% --target-dir %output_directory% -OO -c -s

echo.

echo *** Step 6. Compressing generated files with UPX...
echo.
%full_path_to_upx_exe% %output_directory%\*

echo.

echo *** Step 7. Copy C runtime...
echo.
copy %full_path_to_c_runtime% %output_directory%

echo.

echo *** Step 8. Copy C redistributables...
echo.
copy %full_path_to_c_redist% %output_directory%

echo.

echo *** Step 9. Generate msi using WIX...
echo.
%full_path_to_wix_bin%\candle.exe %full_path_to_wix_script% -out %output_directory%\viri.wixobj
%full_path_to_wix_bin%\light.exe -b %output_directory% %output_directory%\viri.wixobj -out %output_directory%\viri.msi -pdbout %output_directory%\viri.pdbx
echo.