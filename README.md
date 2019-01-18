# Personal Django2.x + Python3 boilerplate

This is my personal boiler plate that holds an empty shell python project with:
- MySQL settings
- Basic reactive CSS template (integrating responsive CSS layer + responsive CCS menu example)
- User management via admin 

### TODO: 
- user registration + activation link sending via email (python)

# INSTALL & FIRST RUN

You have to have python3 installed, then install django using :
pip install Django
pip install --upgrade setuptools  
pip install mysqlclient-1.3.13-cp37-cp37m-win32.whl (from Doc\dev_libs directory from https://www.lfd.uci.edu/~gohlke/pythonlibs/ )
pip install django-simple-email-confirmation  (https://github.com/mfogel/django-simple-email-confirmation)

# CONFIGURATION

You need to edit the settings.py file and create a settings_secret.py from the template provided


# MYSQL CONFIGURATION

This is dependent on your own system, but usually you need to at least create a user and a database

DROP DATABASE django_boilerplate_db;
CREATE DATABASE django_boilerplate_db;
DROP USER 'django_boilerplate_user'@'localhost';
CREATE USER 'django_boilerplate_user2'@'localhost' IDENTIFIED BY 'Fakepwdfordev001';
GRANT SELECT,INDEX,REFERENCES,ALTER,INSERT,UPDATE,DELETE,CREATE,DROP ON django_boilerplate_db.* TO 'django_boilerplate_user2'@'localhost';
FLUSH PRIVILEGES;

# INITIALIZE THE DATA MODEL
python ..\manage.py makemigrations boilerplate
python ..\manage.py migrate boilerplate
python ..\manage.py migrate

# CREATE SUPER-ADMIN 

Additionally you should create a django superadmin user
python manage.py createsuperuser

# RUN 

Following that, you can try running this boilerplate as "python manage.py runserver 8080" and you can then open browser to go to http://localhost:8080

Additionally, because this is MY boiler plate, there will be LiClipse IDE project files inside this repository as that is the free IDE I am using here. 
