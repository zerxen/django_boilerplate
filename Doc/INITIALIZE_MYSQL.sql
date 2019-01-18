DROP DATABASE django_boilerplate_db;
CREATE DATABASE django_boilerplate_db;
DROP USER 'django_boilerplate_user'@'localhost';
CREATE USER 'django_boilerplate_user'@'localhost' IDENTIFIED BY 'fakepwdfordev001';
GRANT SELECT,ALTER,INSERT,UPDATE,DELETE,CREATE ON django_boilerplate_db.* TO 'django_boilerplate_user'@'localhost';
FLUSH PRIVILEGES;
