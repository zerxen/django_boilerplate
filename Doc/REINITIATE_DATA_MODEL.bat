echo "Deleting ANY old migrations"
del "..\django_boilerplate\migrations\0*.py" 


echo "Clean/Recreate MySQL database"
echo drop database django_boilerplate_db; > .\tempsql.sql
echo create database django_boilerplate_db; >> .\tempsql.sql
"C:\Program Files\MySQL\MySQL Server 5.7\bin\mysql.exe" -u root -phegy2CxgD3pyQWJjUjIX < .\tempsql.sql


echo "Create Django Migrations"
python ..\manage.py makemigrations boilerplate
python ..\manage.py migrate boilerplate
python ..\manage.py migrate

pause