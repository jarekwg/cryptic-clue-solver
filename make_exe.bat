:: Remove old build
rmdir build /q /s
:: Create new build
py setup.py build
:: Rename the built directory
ren "build\exe.win32-3.4" CCS
:: Copy across additional dependencies
xcopy dict "build\CCS\dict\" /Y /e /s 
xcopy GUI "build\CCS\GUI\" /Y /e /s 
xcopy keywords "build\CCS\keywords\" /Y /e /s