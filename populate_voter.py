import mysql.connector
import json
import os

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database="election"
)

my_cursor = mydb.cursor()
voter_id = 0

file_list = ['BAGG.txt', 'BMBT.txt', 'BNGA.txt',
             'CEMA.txt', 'CMSA.txt', 'ECOA.txt',
             'ENGA.txt', 'MCBA.txt', 'MCVA.txt',
             'MMFI.txt', 'MTMA.txt', 'PHSA.txt',
             'PLSA.txt', 'SOCA.txt', 'STSA.txt']

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

# print(file_content[0].split(', ')[0][1:].index(": ") + 1)
# print(file_content[0].split(', ')[1])
# print(file_content[0].split(', ')[2])
# print(file_content[0].split(', ')[3])
# print(file_content[0].split(', ')[4])


#['"Name": "Brandon Chater"', '"Roll": "2-09-16-0385"', '"Current Year": "2"', '"Registration Number": "A01-1112-0361-16"', '"Department": "BAGG"']