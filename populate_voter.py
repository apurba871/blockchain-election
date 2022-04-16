# import mysql.connector
import sqlite3
import json
import os
from app import bcrypt

# mydb = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     passwd="",
#     database="election"
# )

'''
my_cursor = mydb.cursor()
voter_id = 0

file_list = ['BAGG.txt', 'BMBT.txt', 'BNGA.txt',
             'CEMA.txt', 'CMSA.txt', 'ECOA.txt',
             'ENGA.txt', 'MCBA.txt', 'MCVA.txt',
             'MMFI.txt', 'MTMA.txt', 'PHSA.txt',
             'PLSA.txt', 'SOCA.txt', 'STSA.txt',
             'BOBA.txt', 'CMEA.txt', 'CMSL.txt',
             'COMA.txt', 'EDUC.txt', 'HISA.txt',
             'MCMF.txt', 'MCMM.txt', 'MCMS.txt',
             'MMCB.txt', 'MPHY.txt']

abs_path = os.path.dirname(os.path.abspath(__file__))
for file in file_list:
    current_file = abs_path + '/student_data/' + file
    with open(current_file, 'r') as f:
        for line in f:
            voter_id += 1
            record = json.loads(line)
            name = record["Name"]
            roll = record["Roll"]
            current_year = record["Current Year"]
            registration_number = record["Registration Number"]
            department = record["Department"]
            # record = line[1:-2].split(', ')
            # name = record[0][record[0].find(':') + 1 : ]
            # roll = record[1][record[1].find(':') + 1 : ]
            # current_year = record[2][record[2].find(':') + 1 : ]
            # registration_number = record[3][record[3].find(':') + 1 : ]
            # department = record[4][record[4].find(':') + 1 : ][2:-1]
            
            # print(name, roll, current_year, registration_number, department)
            # print(department)
            # input()
            my_cursor.execute("INSERT INTO voter (voter_id, voter_cin, voter_name, dept_code) VALUES (%s, %s, %s, %s)", (voter_id, roll, name, department))
mydb.commit()
print("Success, total voters: ", voter_id)
'''
def populate_table():
    file_list = ['BAGG.txt', 'BMBT.txt', 'BNGA.txt',
                'CEMA.txt', 'CMSA.txt', 'ECOA.txt',
                'ENGA.txt', 'MCBA.txt', 'MCVA.txt',
                'MMFI.txt', 'MTMA.txt', 'PHSA.txt',
                'PLSA.txt', 'SOCA.txt', 'STSA.txt',
                'BOBA.txt', 'CMEA.txt', 'CMSL.txt',
                'COMA.txt', 'EDUC.txt', 'HISA.txt',
                'MCMF.txt', 'MCMM.txt', 'MCMS.txt',
                'MMCB.txt', 'MPHY.txt']
    try:
        sqliteConnection = sqlite3.connect('app/site.db')
        cursor = sqliteConnection.cursor()
        print("Successfully Connected to SQLite")

        abs_path = os.path.dirname(os.path.abspath(__file__))
        for file in file_list:
            current_file = abs_path + '/student_data/' + file
            # print(current_file)
            with open(current_file, 'r') as f:
                for line in f:
                    record = json.loads(line)
                    name = record["Name"]
                    cin = record["Roll"]
                    email = cin + '@email.com'
                    # current_year = record["Current Year"]
                    # registration_number = record["Registration Number"]
                    dept = record["Department"]
                    imagefile = 'default.jpg'
                    # password = 'password'
                    password = bcrypt.generate_password_hash('password').decode('utf-8')
                    join_year = 2016
                    is_admin = False
                    item = [cin, name, email, dept, imagefile, password, join_year, is_admin]
                    # print(item)
                    cursor.execute("INSERT INTO voter (cin, name, email, dept, imagefile, password, join_year, is_admin) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", item)
        sqliteConnection.commit()
        print("Successfully populated database!")
        cursor.close()
    except sqlite3.Error as error:
        print("Error while connecting to sqlite", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print("The SQLite connection is closed")

def update_password():
    file_list = ['BAGG.txt', 'BMBT.txt', 'BNGA.txt',
             'CEMA.txt', 'CMSA.txt', 'ECOA.txt',
             'ENGA.txt', 'MCBA.txt', 'MCVA.txt',
             'MMFI.txt', 'MTMA.txt', 'PHSA.txt',
             'PLSA.txt', 'SOCA.txt', 'STSA.txt',
             'BOBA.txt', 'CMEA.txt', 'CMSL.txt',
             'COMA.txt', 'EDUC.txt', 'HISA.txt',
             'MCMF.txt', 'MCMM.txt', 'MCMS.txt',
             'MMCB.txt', 'MPHY.txt']
    try:
        sqliteConnection = sqlite3.connect('app/site.db')
        cursor = sqliteConnection.cursor()
        print("Successfully Connected to SQLite")

        abs_path = os.path.dirname(os.path.abspath(__file__))

        for file in file_list:
            current_file = abs_path + '/student_data/' + file
            # print(current_file)
            with open(current_file, 'r') as f:
                for line in f:
                    record = json.loads(line)
                    # name = record["Name"]
                    cin = record["Roll"]
                    # email = cin + '@email.com'
                    # current_year = record["Current Year"]
                    # registration_number = record["Registration Number"]
                    # dept = record["Department"]
                    # imagefile = 'default.jpg'
                    # password = 'password'
                    password = bcrypt.generate_password_hash('password').decode('utf-8')
                    # join_year = 2016
                    # is_admin = False
                    item = [password, cin]
                    # print(item)
                    cursor.execute("UPDATE voter SET password=? WHERE cin=?", item)
            print(file,"parsed and records updated!")
        sqliteConnection.commit()
        print("Successfully updated database!")
        cursor.close()
    except sqlite3.Error as error:
        print("Error while connecting to sqlite", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print("The SQLite connection is closed")

update_password()

# print(file_content[0].split(', ')[0][1:].index(": ") + 1)
# print(file_content[0].split(', ')[1])
# print(file_content[0].split(', ')[2])
# print(file_content[0].split(', ')[3])
# print(file_content[0].split(', ')[4])


#['"Name": "Brandon Chater"', '"Roll": "2-09-16-0385"', '"Current Year": "2"', '"Registration Number": "A01-1112-0361-16"', '"Department": "BAGG"']