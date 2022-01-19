import pymysql

endpoint = ''
username = 'admin'
password = ''
database_name = 'Transactions_Prod'

connection = pymysql.connect(host = endpoint, user = username, passwd=password, db=database_name)


def lambda_handler(event, context):
    cursor = connection.cursor()
    cursor.execute('SELECT * from Transactions')

    rows = cursor.fetchall()

    for row in rows:
        print("{0} {1} {2}".format(row[0], row[1], row[2]))