import mysql.connector
from gl import local1

def connect():
  if local1 == 0:
    host='mosbachRiddle.mysql.pythonanywhere-services.com'
  else:
    host='localhost'
  conn = mysql.connector.connect(
    user='',
    password='',
    host=host,
    database='mosbachRiddle$default')

  c = conn.cursor()
  return [conn, c]

def close(conn):
  conn.close()
