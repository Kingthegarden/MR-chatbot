import pymysql

endpoint = 'mr-chat-db.cpy6zq2blafd.us-east-2.rds.amazonaws.com'
username = 'admin'
password = 'k1305602!'
database_name = 'Transactions_Prod'

connection = pymysql.connect(host = endpoint, user = username, passwd=password, db=database_name)


def lambda_handler(event, context):
    cursor = connection.cursor()
    cursor.execute('SELECT * from Transactions')

    rows = cursor.fetchall()

    for row in rows:
        print("{0} {1} {2}".format(row[0], row[1], row[2]))