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



Following that, you can try running this boilerplate as "python manage.py runserver 8080" and you can then open browser to go to http://localhost:8080

Additionally, because this is MY boiler plate, there will be LiClipse IDE project files inside this repository as that is the free IDE I am using here. 
