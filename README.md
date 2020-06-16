# README #

## CitizenSocialLab: Housing Dilemma ##

Experiment designed and implemented to be performed in the framework of BiblioLab (Ciència i Acció Ciutadana), a co-created citizen science project with public libraries of Barcelona.

This participatory experiment presents a very common dilemma that studies how we behave in front of a situation of rent a house. The participants (6) have to rent a house in a period of 12 months, they have to decide whether the market price is acceptable or not. Their decisions affect the market and, therefore, to the other participants. This experiment tests different treatments with or without public intervention, with varied endowments and/or initial market prices. 

Note: This experiment is performed in groups of 6 participants.

![](https://github.com/CitizenSocialLab/Housing-Dilemma/blob/master/media/screenshots/ca/JocHabitatge_01.png)

## Data ##
**Not available**  

## Derived Scientific Publications ##
**Not available**  

## Configuration ##
Steps are necessary to get *Housing Dilemma* install, up and running in the local network.

### Creation of the project ###

__Experimental Variables__
Modify the file `vars.py` with the experimental settings:

* `INCREMENT = 5` (increment or decrement of price in each month)
* `MUNICIPI = 'Barcelona'` (municipality, experimental public space)
* `HOUSING_PRICE = 1000` (rental price per month in the municipality)
* `ENDOWMENTS_EQUAL = [2000, 2000, 2000, 2000, 2000, 2000]` (equal endowments for the six partcipants)
* `ENDOWMENTS_UNEQUAL = [1600, 1800, 2000, 2000, 2200, 2400]` (unequal endowments for the six partcipants)
* `LIMIT_HIGH = 1300` (upper limit of the rental price per month)
* `LIMIT_LOW = 700` (lower limit of the rental price per month)
* `SUBSIDY = 47.66` (subsidy in case of participant can afford the rental -limit low- )
* `TAX = 9.53` (tax to other participant to finance subsidy)

__Database MySQL__  
Create MySQL database: name\_db  
Create user database: user\_db  
Create password database: pass\_db

Introduce this information about the database in: `/Housing-Dilemma/settings.py`

__Environment__   
```mkvirtualenv housing ```  

__Requirements__  
```pip install -r requirements.txt```

__MongoDB__  
```mongod --dbpath /.../Housing-Dilemma/ddbb```

__Load text__   
File with text and translations:  `/.../Housing-Dilemma/game/i18n/translations_code.xlsx`  
   
```python excel_to_mongodb.py code```

__Run Server__  
```python manage.py runserver localhost:port```

__Migrations__  
```python manage.py makemigrations```  
```python manage.py migrate```  

### Run project in Local ###

__Step 1: Run MySQL server__  
Run MySQL: `mysql.server start`

__Step 2: Open terminal tabs and work on the environment__  

in Tab 1: MongoDB  
in Tab 2: MySQL  
in Tab 3: Run Application  

Work on environment (in each terminal tab): `workon housing`

__Step 3: Run MongoDB (Tab 1)__  
Run mongodb: `mongod --dbpath /.../Housing-Dilemma/ddbb`

__Step 4: MySQL actions (Tab 2)__

Directory: `cd /.../Housing-Dilemma/`   
Database: `mysql -u user_db -p (pass_db)`

Drop database (if name\_db exits): `drop database name_db;` 
Create database: `create database name_db;`  
Exit: `exit;`

Modificate fields of database: `python manage.py makemigrations`  
Refresh database:
`python manage.py migrate` 

__Step 5: Load texts (Tab 2)__
Load translations: `python excel_to_mongodb.py code`

__Step 6: Run Server (Tab 3)__  
Directory: `cd /.../Housing-Dilemma/ `   
Runserver: `python manage.py runserver localhost:port`

### Access client ###
Client application:  
**http://localhost:port/**  
 
Control and Administration:  
**http://localhost:port/admin**
## Versions ##
Version 1.0

## License ##

CitizenSocialLab is licensed under a [GNU Affero General Public License](https://www.gnu.org/licenses/agpl-3.0.txt)

All the contents of Housing Dilemma repository are under the license [CC BY-NC-SA license](https://creativecommons.org/licenses/by-nc-sa/4.0/)

## Contributors ##

[Julián Vicens](https://jvicens.github.io)

## Contact ##

Julian Vicens: **julianvicens@gmail.com**
