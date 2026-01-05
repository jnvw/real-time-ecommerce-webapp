@echo off
echo ========================================
echo Exporting Data from SQLite Database
echo ========================================
echo.

cd collab_commerce

echo Activating virtual environment...
call ..\env\Scripts\activate.bat

echo.
echo Exporting all data to data_export.json...
python manage.py dumpdata --exclude contenttypes --exclude auth.Permission --exclude sessions --natural-foreign --natural-primary --indent=2 > data_export.json

echo.
echo Exporting users to users.json...
python manage.py dumpdata auth.user --indent=2 > users.json

echo.
echo Exporting shop data to shop_data.json...
python manage.py dumpdata shop --natural-foreign --natural-primary --indent=2 > shop_data.json

echo.
echo ========================================
echo Export Complete!
echo ========================================
echo.
echo Files created:
echo   - data_export.json (all data)
echo   - users.json (users only)
echo   - shop_data.json (shop data only)
echo.
echo Next steps:
echo   1. Copy these JSON files to Railway
echo   2. Run: python manage.py loaddata data_export.json
echo   3. Or import separately: users.json then shop_data.json
echo.
pause

