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

print('PostgreSQL database version:')
cur.execute('SELECT VERSION()')
result = cur.fetchall()
print(result)

print('fetching metadata for a document:')
cur.execute('SELECT DOCUMENT_ID, DOC_NR, CLIENT_NR, ACCOUNT_NR, CLASSIFICATION FROM EDST_CLIENTDOC WHERE DOCUMENT_ID = 215103589')

result = cur.fetchall()
print(result)

# close cursor
cur.close()