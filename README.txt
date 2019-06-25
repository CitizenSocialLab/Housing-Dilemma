mysqldump -u bibliolab -pbibliolab2019 bibliolab  > backups/bibliolab_dump_$(date +"%Y-%m-%d")_$(date +"%T").sql


1. Create the environment
    * cpvirtualenv <nus> <agbar>
2. Create the database
    * mysql -h localhost -u root -p [entrant com a root]
    * create database bibliolab;
    * exit;
    * SequelPro to create user:pass  and give permission: bibliolab:bibliolab2019
    * mysql -ubibliolab -pbibliolab2019
    * drop database bibliolab;
    * create database bibliolab;
3. Project Refractor
    * Copy & Change Names
4. Modify management
5. Create structure database
    * python manage.py migrate
6. Load Texts
    * python excel_to_mongodb.py
    * python excel_to_mongodb.py 'bibliolab'
7. Run MongoDB
    * mongod --dbpath /Users/Julian/Documents/CitizenSocialLab/agbar/bibliolab/db/
    * mongod --dbpath /Users/isabellebonhoure/Desktop/plataformes/agbar/bibliolab/db/
8. Run Server
    * python manage.py runserver 0.0.0.0:8000
9. GIT

NOTES EXPERIMENT:

Station #1: 17 and 01
Station #2: 19 and 22
Station #3: 41 and NN

Partida #7 en adelante sin verificacion.
