import json
import pymysql
from pprint import pprint


def sql_query(query: str, connection):
    """Send sql query to get information
    :param str query: SQL formatted query
    :param connection connection: Connection object to SQL database
    """
    with connection.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()


aisles = {}

user_name = 'root'
database_name = 'loblaws'
password = 'pwd'
cnx = pymysql.connect(user=user_name, database=database_name, password=password)

location_ids = sql_query("SELECT LOCATION_ID FROM loblaws.t_location", cnx)

for location_id in location_ids:
    try:
        number = int(location_id[0][2:4])
    except ValueError:
        continue
    # offset each aisle by 4 units
    number += number * 4
    try:
        height = int(location_id[0][-2:])
        print(height)
    except ValueError:
        continue
    # Each aisle is 20 units long, decided to do a 10 unit offset
    aisles[location_id[0]] = [(number, number + 1), (10, 30), height]

pprint(aisles)
with open('aisle.json', 'w') as f:
    f.write(json.dumps(aisles))
