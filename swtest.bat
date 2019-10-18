@echo off

SET test_path=%1
SET browser=%2
if "%browser%"=="" set "browser=gc"

set hour=%time:~0,2%
if "%hour:~0,1%" == " " set hour=0%hour:~1,1%
set min=%time:~3,2%
if "%min:~0,1%" == " " set min=0%min:~1,1%
set secs=%time:~6,2%
if "%secs:~0,1%" == " " set secs=0%secs:~1,1%
set year=%date:~-4%
set month=%date:~4,2%
if "%month:~0,1%" == " " set month=0%month:~1,1%
set day=%date:~7,2%
set run_time=%hour%%min%%secs%_%month%%day%%year%


if not x%test_path:::=%==x%test_path% GOTO run_whole_class

if x%test_path:::=%==x%test_path% GOTO run_one_test

:run_whole_class
FOR /f "tokens=1,2,3,4 delims=::" %%a IN ("%test_path%") do SET test_name=%%c
pytest -s -v %test_path% --html reports/%test_name%_%run_time%.html --browser %browser%
GOTO end

:run_one_test
FOR /f "tokens=1,2,3,4 delims=/" %%a IN ("%test_path%") do SET test_name=%%c
SET class_name=%test_name:~0,-3%
pytest -s -v %test_path% --html reports/%class_name%_%run_time%.html --browser %browser%
GOTO end

:end
