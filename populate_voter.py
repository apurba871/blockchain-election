import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database="election"
)

my_cursor = mydb.cursor()
voter_id = 0

#trying to add all students of BAGG into voter table
with open('BAGG.txt', 'r') as bagg:
    for line in bagg:
        voter_id += 1

        record = line[1:-2].split(', ')
        name = record[0][record[0].find(':') + 1 : ]
        roll = record[1][record[1].find(':') + 1 : ]
        current_year = record[2][record[2].find(':') + 1 : ]
        registration_number = record[3][record[3].find(':') + 1 : ]
        department = record[4][record[4].find(':') + 1 : ][2:-1]
        # print(name, roll, current_year, registration_number, department)
        # print(department)

        my_cursor.execute("INSERT INTO voter (voter_id, voter_cin, voter_name, dept_code) VALUES (%s, %s, %s, %s)", (voter_id, roll, name, department))
mydb.commit()
print("Success")

# print(file_content[0].split(', ')[0][1:].index(": ") + 1)
# print(file_content[0].split(', ')[1])
# print(file_content[0].split(', ')[2])
# print(file_content[0].split(', ')[3])
# print(file_content[0].split(', ')[4])


#['"Name": "Brandon Chater"', '"Roll": "2-09-16-0385"', '"Current Year": "2"', '"Registration Number": "A01-1112-0361-16"', '"Department": "BAGG"']