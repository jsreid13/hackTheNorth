import json
import requests
from pprint import pprint
import pymysql


def sql_query(query: str, connection):
    """Send sql query to get information
    :param str query: SQL formatted query
    :param connection connection: Connection object to SQL database
    """
    with connection.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()


product_name = "apple"
product_name = product_name.replace(' ', '-')[:40]
#  print((dept_name, product_name))
url = "https://gateway-staging.ncrcloud.com/catalog/items?itemCodePattern=%s" % product_name

user = "acct:groceryfinder2-stg@groceryfinder2serviceuser"
app_key = "8a0084a165d712fd0165e0b07e830012"
pwd = ''  # Use password you provided when you created your NCR profile

headers = {'Accept': "application/json",
           'Content-Type': "application/json",
           'nep-service-version': "2.2.1:2",
           'nep-application-key': app_key
           }

res = requests.get(url, headers=headers, auth=(user, pwd))
try:
    pprint(json.loads(res.text)['pageContent'][0]['departmentId'])
except (KeyError, IndexError):
    print(product_name)
    pprint(json.loads(res.text))
