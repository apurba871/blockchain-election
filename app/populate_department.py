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
my_cursor.execute("INSERT INTO department VALUES ('BOBA', 'BOBA dept')")
my_cursor.execute("INSERT INTO department VALUES ('CMEA', 'CMEA dept')")
my_cursor.execute("INSERT INTO department VALUES ('CMSL', 'CMSL dept')")
my_cursor.execute("INSERT INTO department VALUES ('COMA', 'COMA dept')")
my_cursor.execute("INSERT INTO department VALUES ('EDUC', 'EDUC dept')")
my_cursor.execute("INSERT INTO department VALUES ('HISA', 'HISA dept')")
my_cursor.execute("INSERT INTO department VALUES ('MCMF', 'MCMF dept')")
my_cursor.execute("INSERT INTO department VALUES ('MCMM', 'MCMM dept')")
my_cursor.execute("INSERT INTO department VALUES ('MCMS', 'MCMS dept')")
my_cursor.execute("INSERT INTO department VALUES ('MMCB', 'MMCB dept')")
my_cursor.execute("INSERT INTO department VALUES ('MPHY', 'MPHY dept')")

mydb.commit()
print("Success")