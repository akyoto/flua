@rem Switching echo off will make the setup look a bit better
@echo off
if "%1"=="/?" (
	echo Blitzprog Windows installation for MinGW V. 1
	echo *********************************************
	echo.
	echo This setup will install Blitzprog for your MinGW -- Minimalistic GNU for Windows -- installation. If you do not use MinGW, this is not the right setup for you. If it is, you can use this setup to easily configure MinGW for use with Blitzprog.
	echo.
	echo All necessary files will be copied to your MinGW installation. If you do not want that to happen, you have to set it up manually: have a look at the README file.
	echo.
	echo Command line options:
	echo - /?        Show this help.
	echo - uninstall Remove Blitzprog
	exit /B 0
) else if "%1"=="uninstall" (
	call :uninstall
) else (
	call :install
)
exit /B 0

rem This function will install Blitzprog
:install
	echo you are installing Blitzprog on your MinGW installation.
	choice /CYN /T:Y,5 Continue installation (Default after five seconds) 
	if %errorlevel% == 2 (
		goto :notInstalled
	)
	call :getMinGW
	echo starting installation...
	xcopy ..\..\lib\* %mingw_dir%\include /E
	xcopy ..\..\lib32\libblitzprog.a %mingw_dir%\lib
	xcopy ..\..\bin32\bp.exe %mingw_dir%\bin
	echo.
	echo Blitzprog has been successfully installed.
	exit /B 0

:uninstall
	echo you are installing Blitzprog on your MinGW installation.
	choice /CYN Continue removal
	if %errorlevel% == 2 (
		goto :notInstalled
	)
	call :getMinGW
	echo starting removal...
	del %mingw_dir%\include\Blitzprog /S /Q
	del %mingw_dir%\include\header.hpp
	del %mingw_dir%\lib\libblitzprog.a
	del %mingw_dir%\bin\bp.exe
	echo.
	echo Blitzprog has been successfully removed.
	exit /B 0

rem This one is called once a failure occurs. It gives back a 
:failure
	call :notInstalled
	if defined %1 (
		exit /B %1
	) else (
		exit /B 1
	)

rem This block is called from every part of the script that aborts the installation.
:notInstalled
	echo *********************************************
	echo Setup aborted, no files were touched.
	echo on
	exit /B

rem Determines the MinGW installation
:getMinGW
	if not defined mingw_dir (
		if exist C:\MinGW (
			set mingw_dir=C:\MinGW
		) else if exist D:\Programme\MinGW (
			set mingw_dir=%ProgramFiles%\MinGW
		) else (
			echo Error: I could not detect your MinGW installation. Pleace set it by specifying %mingw_dir%. Remember: Type "set mingw_dir=..." is enough, the variable will be deleted when you close the command line.
			rem Fehlercode 2: MinGW not found.
			goto :failure 2	
		)
	)
	echo MinGW found at %mingw_dir%
	exit /B 0
