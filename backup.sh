echo off
echo dumping full data
docker exec compose_mysql_1 sh -c 'exec mysqldump --add-drop-database -uroot -pwortel -B md_directory -P3307' > ../md_directory_full_data/db_backup_mddir.sql
echo dumping db structure
docker exec compose_mysql_1 sh -c 'exec mysqldump --add-drop-database -d -uroot -pwortel -B md_directory -P3307' > db_structure_mddir.sql
echo committing public repo
hg commit --message "$1"
cd ../md_directory_full_data/
echo committing private repo
hg commit --message "$1"
cd ../md_directory
