#!/bin/bash

# CONFIGURATION
MUSER="django_boilerplate_user2"
MPASS="Fakepwdfordev001"
MDB="django_boilerplate_db"
 
# Detect paths
MYSQL=$(which mysql)
AWK=$(which awk)
GREP=$(which grep)

# EXECUTION OF MAIN
cd "$(dirname "$0")"

echo "==========================="
echo "Deleting ANY old migrations"
echo "==========================="
rm -rf ../boilerplate/migrations/0*.py 

echo "============================="
echo "Clean/Recreate MySQL database"
echo "============================="

TABLES=$($MYSQL -u $MUSER -p$MPASS $MDB -e 'show tables' | $AWK '{ print $1}' | $GREP -v '^Tables' )
for t in $TABLES
do
        echo "Deleting $t table from $MDB database..."
        $MYSQL -u $MUSER -p$MPASS $MDB -e "SET FOREIGN_KEY_CHECKS=0; DROP table $t ; SET FOREIGN_KEY_CHECKS=1;"
done

echo "========================"
echo "Create Django Migrations"
echo "========================"
python3 ../manage.py makemigrations boilerplate
python3 ../manage.py migrate

