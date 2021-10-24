How to run our project:
python == 3.8
dash == 1.13.3 
pandas == 1.0.5
pymongo == 3.11.2
pysqlite3 == 0.4.6

for the first main widget:
1. cd phone/
2. python3 -m venv venv
4. source venv/bin/activate
5. python -m pip install dash==1.13.3 pandas==1.0.5
6. python3 app_phone.py
7. go to http://localhost:8050

for the other two widgets, run:
- cd phone/
- python3 bar_phone.py
- python3 dot_phone.py

For the second part of the project, go to phone_grid
for the grid view utilizing mongodb database,
run:
python grid_phone_mongodb.py

for the gird view utilizing sql database,
run:
python grid_phone_sql.py

Before running the two files, you will have to set up mongodb database and sql database and load 20191226-items.csv into the database.

For MongoDB, set up local mongodb database using the tutorial https://docs.mongodb.com/manual/tutorial/install-mongodb-on-os-x/
To load the csv file in MongoDB, use the following command:
mongoimport --type csv -d test -c products --headerline --drop 20191226-items.csv
Please make sure that this commend is run under the directory that contains the csv file

For SQLite, set up local sqlite database by first downloading local sqlite database https://www.sqlite.org/download.html. After runing the install.sh, the sqlite tools should be installed.
Then under the directory phone_grid run the following command:
sqlite3 products.pd will run the local SQL database that contains all the data.
