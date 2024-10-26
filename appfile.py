#!/usr/bin/python3

# https://mosbachriddle.pythonanywhere.com/

import random

from flask import Flask, request, make_response

import db
import gl # globals
import h # html

#FLASK INIT
app = Flask(__name__)

@app.route('/beenden')
def beenden():
  html = '''<p>Willst du das Spiel wirklich beenden?</p>
  <form action="/logout" method="get"><input type="submit" value="Spiel beenden"></form>
  <form action="/play" method="get"><input type="submit" value="Spiel fortsetzen"></form>
  '''
  return h.head + html + h.tail

@app.route('/logout')
def logout():
  html = '<p>Spiel wurde beendet.<br>Cookie mit Spielstand gelöscht.</p><form action="/" method="get"><input type="submit" value="Zur Startseite"></form>\n'
  resp = make_response(h.head + html + h.tail)
  resp.delete_cookie('game')
  return resp

@app.route('/')
def index():
  game = gl.read_cookie(request)

  if game[0]:
    html = '''<p><b>Du spielst bereits</b>:</p>
    <form action="/play" method="get"><input type="submit" value="Spiel fortsetzen"></form>
    <form action="/beenden" method="get"><input type="submit" value="Spiel beenden"></form>
    '''
    
    return h.head + html + h.tail


  html = '''<p>Willkommen im Escape Room der Stadt Mosbach. Deine Aufgabe wird es sein, ein paar ausgewählte Rätsel zu lösen, um das Spiel zu beenden. Die Rätsel befinden sich alle nur wenige Gehminuten von dem Marktplatz entfernt. Zum Spielen taugt jedes Smartphone oder Tablet. Folge einfach den Hinweisen auf der Seite, besuche den Ort und sende die richtige Antwort ab.</p>
  
  <p>Die Karten und Bilder werden beim Draufklicken größer angezeigt.</p>

  <p>Wenn du alle Rätsel gelöst hast, wirst du am Ende mit einem <b>Code</b> belohnt.</p>

  <form action="/play" method="get"><input type="submit" value="Spiel starten"></form>
  '''
  
  return h.head + h.template_start("Marktplatz", "00_marktplatz_karte.png", "00_marktplatz.jpg", html) + h.tail


@app.route('/play')
def play():
  flag, game = gl.read_cookie(request)
  
  if not(flag):
    # Starte neues Spiel
    print("Start new game")

    # Choose 5 riddles randomly of all riddles
    conn, c = db.connect()
    sql = "select id from riddle where active = 1"
    c.execute(sql)
    result = c.fetchall()

    list1 = []
    for i in result:
      list1.append(i[0])
    
    random.shuffle(list1)

    # Create randomized riddle order and with start value 1 at the end
    cookie_content = gl.number_to_cookie(list1[0:5] + [1])[1]

    # Get first riddle and render first page
    sql = "select id, title, address, map, picture, text1, max, answer from riddle where id = %s"
    c.execute(sql, [list1[0]]) # Waehle erstes Raetsel
    result = c.fetchone()
    db.close(conn)

    html = h.head + h.template_riddle(
      result[0], #id
      result[1], #title
      result[2], #address
      result[3], #map
      result[4], #picture
      result[5], #content
      1, #current (new game)
      result[6], #max
      result[7] #answer
    ) + h.tail
    
    resp = make_response(html)
    resp.set_cookie('game', cookie_content)

    return resp


  # Cookie found, Game is running
  conn, c = db.connect()
  sql = "select max from riddle limit 1"
  c.execute(sql)
  max = c.fetchone()[0]

  try:
    pos = game[game[-1]-1]
  except:
    return h.head + 'Cookie korrput. Beginne neues Spiel. <form action="/logout" method="get"><input type="submit" value="Spiel beenden"></form>' + h.tail

  #print("POS: " + str(pos))
  #print("GAME: " + gl.game2str(game))

  # Game over?
  if game[-1] > max:
    c.execute("select code from riddle limit 1")
    result = c.fetchone()[0]
    db.close(conn)
    html = []
    html.append('<p>Herzlichen Glückwunsch, du hast das Spiel erfolgreich beendet!</p>\n')
    html.append('<p>Der Gewinn-Code lautet: <b>'+result+'</b></p>\n<form action="/logout" method="get"><input type="submit" value="Spiel neustarten"></form>\n')
    return h.head + ''.join(html) + h.tail

  # Get actual riddle and render page
  sql = "select id, title, address, map, picture, text1, max, answer from riddle where id = %s"
  c.execute(sql, [pos])
  result = c.fetchone()
  db.close(conn)

  if result == None:
    return h.head + '\nCookie korrput. Beginne neues Spiel. <form action="/logout" method="get"><input type="submit" value="Spiel beenden"></form>\n' + h.tail

  html = h.head + h.template_riddle(
    result[0], #id
    result[1], #title
    result[2], #address
    result[3], #map
    result[4], #picture
    result[5], #content
    game[-1], #current
    result[6], #max
    result[7] #answer
  ) + h.tail

  #resp.set_cookie('game', cookie_content)
  resp = make_response(html)
  return resp
  
@app.route('/checkAnswer')
def checkAnswer():
  # Waere nicht noetig, kann aus Cookie gelesen werden!
  id = gl.filter_only_characters_and_nr(request.args.get('id', ''))
  if len(id) == 0:
    return "Error: len(id) = 0"
  
  answer = gl.filter_only_characters_and_nr(request.args.get('answer', ''))
  if len(answer) == 0:
    return h.head + '<p>Keine Antwort eingegeben.</p><button onclick="history.back()">Zurück</button>' + h.tail

  conn, c = db.connect()
  sql = "select answer from riddle where id = %s"
  c.execute(sql, [id])
  result = c.fetchone()
  db.close(conn)

  if result[0] == answer:
    flag, game = gl.read_cookie(request)

    if not(flag):
      return h.head + 'Cookie korrput. Beginne neues Spiel. <form action="/logout" method="get"><input type="submit" value="Spiel beenden"></form>' + h.tail

    game[-1] += 1
    
    html = h.head + '<p>Die Eingabe <b>'+ answer +'</b> ist korrekt!</p><form action="/play" method="get"><input type="submit" value="Spiel fortsetzen"></form>' + h.tail
    resp = make_response(html)
    resp.set_cookie('game', gl.number_to_cookie(game)[1])
    return resp
  else:
    return h.head + '<p>Die Antwort <b>'+ answer +'</b> ist leider nicht korrekt.</p><button onclick="history.back()">Zurück</button>' + h.tail


@app.route('/admin')
def admin():
  pass


@app.route('/create')
def create():
  conn, c = db.connect()
  c.execute("DROP TABLE IF EXISTS riddle")
  c.execute(db.riddle_table)
  conn.commit()

  sql = "INSERT INTO riddle(id, title, address, map, picture, text1, active, type1, answer, code, max) VALUES(%s, %s, %s, %s, %s, %s, 1, 0, %s, %s, %s)"
  
  c.executemany(sql, db.riddle)
  
  #for i in db.riddle:
  #  print(i)
  #  c.execute(sql, i)

  conn.commit()
  db.close(conn)

  return "Table deleted and created."