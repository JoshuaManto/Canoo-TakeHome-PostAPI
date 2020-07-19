import json
import pymysql
import os

#Configuration Values

endpoint = os.environ['HOST']
username = os.environ['USER']
password = os.environ['PASS']
database_name = os.environ['DBNAME']

#Connection To Database
try:
    connection = pymysql.connect(endpoint, user=username, passwd=password, db=database_name)
    print('****connected to db****')
except:
    print('Error in connecting to db')

# POST REQUEST
def addLogs(event, context):

    # Get payload from event body
    # Should be an array of objects
    payload = event['payload']

    # SQL Query to add 1 or more error log/s
    query = 'INSERT INTO Logs (device_id, error_number, time_stamp) VALUES (%s, %s, %s)'

    # Build data to be inserted to the database
    # Array of tuples
    data = []
    for row in payload:
        data.append((row['deviceID'], row['err'], row['timestamp']))

    # Query Execution
    cursor = connection.cursor()

    # Handles 1 or more incoming data
    if(len(data) == 1):
        # print('1 data')
        # print(data)
        # print(data[0])
        cursor.execute(query, data[0])
    elif(len(data) > 1):
        # print('2 or more data')
        cursor.executemany(query, data)

    connection.commit()

    # Response body
    body = {
        "result": "Success. {0} number of data inserted".format(cursor.rowcount)
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response
