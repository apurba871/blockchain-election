from dataclasses import dataclass
import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database="election"
)

my_cursor = mydb.cursor()

my_cursor.execute("INSERT INTO department VALUES ('BAGG', 'B.A. General')")
my_cursor.execute("INSERT INTO department VALUES ('BNGA', 'Bengali Hons')")
my_cursor.execute("INSERT INTO department VALUES ('BMBT', 'Biotechnology')")
my_cursor.execute("INSERT INTO department VALUES ('CEMA', 'Chemistry Hons')")
my_cursor.execute("INSERT INTO department VALUES ('CMSA', 'Computer Sc. Hons')")
my_cursor.execute("INSERT INTO department VALUES ('ECOA', 'Economics Hons')")
my_cursor.execute("INSERT INTO department VALUES ('ENGA', 'English Hons')")
my_cursor.execute("INSERT INTO department VALUES ('MCVA', 'Mass Communication')")
my_cursor.execute("INSERT INTO department VALUES ('MTMA', 'Mathematics Hons')")
my_cursor.execute("INSERT INTO department VALUES ('MCBA', 'Microbiology Hons')")
my_cursor.execute("INSERT INTO department VALUES ('MMFI', 'Multimedia')")
my_cursor.execute("INSERT INTO department VALUES ('PHSA', 'Physics Hons')")
my_cursor.execute("INSERT INTO department VALUES ('PLSA', 'Political Sc. Hons')")
my_cursor.execute("INSERT INTO department VALUES ('STSA', 'Statistics Hons')")
my_cursor.execute("INSERT INTO department VALUES ('SOCA', 'Sociology Hons')")

mydb.commit()
print("Success")