#!/usr/bin/python3

# https://mosbachriddle.pythonanywhere.com/

import random

from flask import Flask, request, make_response, render_template

import db
import gl #globals

#FLASK INIT
app = Flask(__name__)

@app.route('/beenden')
def beenden():
  html= '''<p>Willst du das Spiel wirklich beenden?</p>
  <form action="/logout" method="get"><input type="submit" value="Spiel beenden"></form>
  <form action="/play" method="get"><input type="submit" value="Spiel fortsetzen"></form>
  '''
  return render_template('empty.html', content=html)

@app.route('/logout')
def logout():
  html = render_template('empty.html', content='<p>Spiel wurde beendet.<br>Cookie mit Spielstand gelöscht.</p><form action="/" method="get"><input type="submit" value="Zur Startseite"></form>\n')
  resp = make_response(html)
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
    
    return render_template('empty.html', content=html)


  html = '''<p>Willkommen im Escape Room der Stadt Mosbach. Deine Aufgabe wird es sein, ein paar ausgewählte Rätsel zu lösen, um das Spiel zu beenden. Die Rätsel befinden sich alle nur wenige Gehminuten von dem Marktplatz entfernt. Zum Spielen taugt jedes Smartphone oder Tablet. Folge einfach den Hinweisen auf der Seite, besuche den Ort und sende die richtige Antwort ab.</p>
  
  <p>Die Karten und Bilder werden beim Draufklicken größer angezeigt.</p>

  <p>Wenn du alle Rätsel gelöst hast, wirst du am Ende mit einem <b>Code</b> belohnt.</p>

  <form action="/play" method="get"><input type="submit" value="Spiel starten"></form>
  '''
   
  return render_template('start.html',
                         address='Marktplatz',
                         map='00_marktplatz_karte.png',
                         picture='00_marktplatz.jpg',
                         content=html)


@app.route('/play')
def play():
  flag, game = gl.read_cookie(request)
  
  if not(flag):
    # Starte neues Spiel
    
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

    html = render_template('riddle.html',
                    id=result[0],
                    title=result[1],
                    address=result[2],
                    map=result[3],
                    picture=result[4],
                    content=gl.render_riddle(result[5]),
                    current=1,
                    max=result[6],
                    answer=result[7])
    
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
    return render_template('empty.html', content='Cookie korrput. Beginne neues Spiel. <form action="/logout" method="get"><input type="submit" value="Spiel beenden"></form>')

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
    return render_template('empty.html', content=''.join(html))

  # Get actual riddle and render page
  sql = "select id, title, address, map, picture, text1, max, answer from riddle where id = %s"
  c.execute(sql, [pos])
  result = c.fetchone()
  db.close(conn)

  if result == None:
    return render_template('empty.html', content='Cookie korrput. Beginne neues Spiel. <form action="/logout" method="get"><input type="submit" value="Spiel beenden"></form>')

  html = render_template('riddle.html',
                  id=result[0],
                  title=result[1],
                  address=result[2],
                  map=result[3],
                  picture=result[4],
                  content=gl.render_riddle(result[5]),
                  current=game[-1],
                  max=result[6],
                  answer=result[7])

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
    return render_template('empty.html', content='<p>Keine Antwort eingegeben.</p><button onclick="history.back()">Zurück</button>')

  conn, c = db.connect()
  sql = "select answer from riddle where id = %s"
  c.execute(sql, [id])
  result = c.fetchone()
  db.close(conn)

  if result[0] == answer:
    flag, game = gl.read_cookie(request)

    if not(flag):
      return render_template('empty.html', content='Cookie korrput. Beginne neues Spiel. <form action="/logout" method="get"><input type="submit" value="Spiel beenden"></form>')

    game[-1] += 1
    
    html = render_template('empty.html', content='<p>Die Eingabe <b>'+ answer +'</b> ist korrekt!</p><form action="/play" method="get"><input type="submit" value="Spiel fortsetzen"></form>')
    resp = make_response(html)
    resp.set_cookie('game', gl.number_to_cookie(game)[1])
    return resp
  else:
    return render_template('empty.html', content='<p>Die Antwort <b>'+ answer +'</b> ist leider nicht korrekt.</p><button onclick="history.back()">Zurück</button>')

@app.route('/showDB')
def showDB():
  conn, c = db.connect()

  sql = "select * from mc"
  c.execute(sql)
  result = c.fetchall()

  db.close(conn)

  return "Table deleted and created."


@app.route('/admin')
def admin():
  pass




@app.route('/checkDB')
def checkDB():
  html = []
 
  conn, c = db.connect()
  html.append("c: ")
  html.append(str(gl.filter_only_characters_and_nr(str(c))))
  html.append("<br />\nconn: ")
  html.append(str(gl.filter_only_characters_and_nr(str(conn))))
 
  db.close(conn)
 
  return "".join(html)

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