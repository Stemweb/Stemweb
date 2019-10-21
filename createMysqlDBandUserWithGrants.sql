export MY_USER=stemweb
export MY_PASSW=ChangeMe
export MY_HOST=localhost
export MY_DB=stemwebdb_v1
mysql -u root -e "CREATE USER '$MY_USER'@'$MY_HOST' IDENTIFIED BY '$MY_PASSW'"
mysql -u root -e "CREATE DATABASE $MY_DB"
mysql -u root -e "GRANT ALL ON *.* TO '$MY_USER'@'$MY_HOST'"
mysql -u root -e "GRANT USAGE ON *.* TO '$MY_USER'@'$MY_HOST'"
mysql -u root -e "FLUSH PRIVILEGES"
mysql -D $MY_DB -u $MY_USER -p$MY_PASSW -e "SET GLOBAL FOREIGN_KEY_CHECKS = 0"
