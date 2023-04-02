import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DB_USERNAME = os.getenv('POSTGRES_USER')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD')
DB_DATABASE = os.getenv('POSTGRES_DB')

conn = psycopg2.connect("host=localhost port=5432 dbname=%s user=%s password=%s"%(DB_DATABASE, DB_USERNAME, DB_PASSWORD))

# create a cursor
cur = conn.cursor()

# execute a statement
print('PostgreSQL database version:')
cur.execute('SELECT DOCUMENT_ID, DOC_NR, CLIENT_NR, ACCOUNT_NR, CLASSIFICATION FROM EDST_CLIENTDOC WHERE DOCUMENT_ID = 215103589')

# display the PostgreSQL database server version
db_version = cur.fetchall()
print(db_version)

cur.close()