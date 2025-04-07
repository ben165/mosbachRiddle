#!/usr/bin/python3

# https://mosbachriddle.pythonanywhere.com/

import random, time, hashlib, uuid
from os import listdir, remove, getcwd
from os.path import exists, isdir

from gl import local1

from flask import Flask, request, make_response
from PIL import Image

import db
import gl # globals
import h # html

#FLASK INIT
app = Flask(__name__)

#PYTHONANYWHERE
if local1 == 0:
  pic_path = "mysite/static/img/riddle/"
else:
  pic_path = "static/img/riddle/"

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
  resp.delete_cookie('ts')
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
  
  return h.head + h.template_start("Marktplatz", "marktplatz_karte.png", "marktplatz.jpg", html) + h.tail


@app.route('/play')
def play():
  flag, game = gl.read_cookie(request)
  
  if not(flag):
    # Starte neues Spiel
    
    # Choose X riddles randomly of all riddles
    conn, c = db.connect()
    sql = "select id from riddle where active = 1"
    c.execute(sql)
    result = c.fetchall()

    list1 = []
    for i in result:
      list1.append(i[0])
    
    random.shuffle(list1)

    # Create randomized riddle order and with start value 0 (pos is at the end)
    # 
    # gl.number_to_cookie(list1[0:gl.max_riddle] + [0])[1] # For limited amount of riddles per game
    
    cookie_content = gl.number_to_cookie(list1 + [0]) # all riddles
    if cookie_content[0] == False:
      db.close(conn)
      return h.head + "<p>System was not able to create games out of SQL query.</p>" + h.tail
    cookie_content = cookie_content[1]

    # Get first riddle and render first page
    sql = "select id, title, address, map, picture, text1, answer, delay from riddle where id = %s"
    c.execute(sql, [list1[0]]) # Waehle erstes Raetsel
    result = c.fetchone()
    db.close(conn)

    # Get current time stamp
    ts = str(int( time.time() ))

    html = h.head + h.template_riddle(
      result[0], #id
      result[1], #title
      result[2], #address
      result[3], #map
      result[4], #picture
      result[5], #content
      0, #current (new game)
      len(list1), #max riddles
      result[6], #answer
      ts, #timestamp str
      result[7] #delay int
    ) + h.tail
    
    resp = make_response(html)
    resp.set_cookie('game', cookie_content)
    resp.set_cookie('ts', ts)

    return resp


  # Cookie found, Game is running
  max = len(game)-1

  try:
    current = game[-1]
    pos = game[current]
  except:
    return h.head + 'Cookie korrput. Beginne neues Spiel. <form action="/logout" method="get"><input type="submit" value="Spiel beenden"></form>' + h.tail    

  #print("POS: " + str(pos))
  #print("GAME: " + gl.game2str(game))

  # Game over?
  conn, c = db.connect()
  if game[-1] >= max:    
    c.execute("select code from riddle limit 1")
    result = c.fetchone()[0]
    db.close(conn)
    html = []
    html.append('<p>Herzlichen Glückwunsch, du hast das Spiel erfolgreich beendet!</p>\n')
    html.append('<p>Der Gewinn-Code lautet: <b>'+result+'</b></p>\n<form action="/logout" method="get"><input type="submit" value="Spiel neustarten"></form>\n')
    return h.head + ''.join(html) + h.tail

  # Get actual riddle and render page
  sql = "select id, title, address, map, picture, text1, answer, delay from riddle where id = %s"
  c.execute(sql, [pos])
  result = c.fetchone()
  db.close(conn)

  if result == None:
    return h.head + '\nCookie korrput (Raetsel nicht gefunden). Beginne neues Spiel. <form action="/logout" method="get"><input type="submit" value="Spiel beenden"></form>\n' + h.tail

  flag2, ts = gl.read_ts_cookie(request)
  if not(flag2): # Ts cookie corrupt oder nicht mehr da :(
    ts = str(int( time.time() ))

  html = h.head + h.template_riddle(
    result[0], #id
    result[1], #title
    result[2], #address
    result[3], #map
    result[4], #picture
    result[5], #content
    game[-1], #current riddle
    len(game)-1, #max riddles
    result[6], #answer
    ts, #timestamp str
    result[7]
  ) + h.tail

  #resp.set_cookie('game', cookie_content)
  resp = make_response(html)

  if not(flag2):
    resp.set_cookie('ts', ts)

  return resp
  
@app.route('/checkAnswer')
def checkAnswer():
  # Waere nicht noetig, kann aus Cookie gelesen werden!
  id = gl.filter_only_numbers(request.args.get('id', ''))
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

  # Eingabe korrekt
  if result[0] == answer:
    flag, game = gl.read_cookie(request)

    if not(flag):
      return h.head + 'Cookie korrput. Beginne neues Spiel. <form action="/logout" method="get"><input type="submit" value="Spiel beenden"></form>' + h.tail

    game[-1] += 1
    
    html = h.head + '<p>Die Eingabe <b>'+ answer +'</b> ist korrekt!</p><form action="/play" method="get"><input type="submit" value="Spiel fortsetzen"></form>' + h.tail
    resp = make_response(html)
    resp.set_cookie('game', gl.number_to_cookie(game)[1]) # move one riddle forward
    resp.set_cookie('ts', str(int( time.time() ))) # change current timestamp
    return resp
  else:
    return h.head + '<p>Die Antwort <b>'+ answer +'</b> ist leider nicht korrekt.</p><button onclick="history.back()">Zurück</button>' + h.tail


@app.route('/admin')
def admin():
  html = []
  html.append("<h4>Login Admin Panel</h4>\n")
  html.append("<form action=\"/adminLogin\" method=\"post\">Passwort:<br>\n<input type=\"password\" name=\"password\"><br>\n<input type=\"submit\" value=\"Abschicken\">\n</form>")

  return h.head + "".join(html) + h.tail


@app.route('/adminLogin', methods=['POST'])
def adminLogin():

  pwHash = request.form.get("password").encode('utf-8')
  pwHash = hashlib.sha256(pwHash).hexdigest()

  if not(pwHash == gl.pw1):
    return h.head + 'Wrong password. <a href="/admin">Go back</a>.' + h.tail
  
  html = []
  html.append("Login erfolgreich.<br><br>\n")
  html.append("<ul>\n<li><a href=\"/adminPanel\">Admin-Panel</a></li>\n")
  html.append("<li><a href=\"/adminLogout\">Logout</a></li>\n</ul>\n")

  # Create session for login (saved in cookie and db)
  resp = make_response(h.head + ''.join(html) + h.tail)
  session = uuid.uuid4().hex
  resp.set_cookie('session', session)
  
  conn, c = db.connect()
  sql = "update other set session = %s where id=1"
  c.execute(sql, [session])
  conn.commit()
  db.close(conn)

  return resp

@app.route('/adminPanel')
def adminPanel():
  #Check session
  conn, c = db.connect()
  if not(gl.checkSession(request, c)):
    db.close(conn)
    return h.head + "Session does not match. Back to <a href=\"/admin\">Login</a>." + h.tail
  db.close(conn)

  html = []
  html.append("<h3>Admin Panel</h3>\n")
  html.append('<a href="/adminPanelChooseRiddle">Rätsel löschen</a><br>\n')
  html.append('<a href="/deactivateRiddle">Rätsel de/aktivieren</a><br>\n')
  html.append('<a href="/newRiddle">Neues Rätsel anlegen</a><br><br>\n')

  html.append('<a href="/pictures">Bild löschen</a><br>\n')
  html.append('<a href="/pictureUpload">Bild hochladen</a><br><br>\n')

  html.append('<a href="/editDelay">Wartezeit für mehr Infos ändern</a><br><br>\n')

  html.append('<a href="/editCode">Lösungswort ändern</a><br><br>\n')

  html.append('<a href="/adminLogout">Logout</a><br>\n')

  return h.head + ''.join(html) + h.tail

@app.route('/adminPanelChooseRiddle')
def adminPanelChooseRiddle():
  #Check session
  conn, c = db.connect()
  if not(gl.checkSession(request, c)):
    db.close(conn)
    return h.head + "Session does not match. Back to <a href=\"/admin\">Login</a>." + h.tail
  
  sql = "select id, title from riddle"
  c.execute(sql)
  result = c.fetchall()
  
  html = []
  html.append("<p>Wähle Rätsel aus (ID), welches du löschen möchtest. Zum <a href=\"/adminPanel\">Admin-Panel</a>.</p>\n")
  html.append("<table>\n")
  html.append("<tr><th>ID</th><th>Titel</th><th>Play</th></tr>\n")
  for i in result:
    html.append("<tr><td><a href=\"adminDeleteRiddle/"+ str(i[0]) +"\">"+ str(i[0]) +"</a></td><td>"+ i[1] +"</td><td><a href=\"debugPlay/"+ str(i[0]) +"\">Play</a></td></tr>\n")
  html.append("</table>")

  db.close(conn)

  return h.head + ''.join(html) + h.tail

@app.route('/debugPlay/<id>')
def debugPlay(id):
  id = gl.filter_only_numbers(id)
  if len(id) == 0:
    return "Falsche Eingabe"
  
  html = h.head + "Rätsel <b>"+ id +"</b> ist jetzt aktiv. Gehe zurück zu <a href=\"/play\">/play</a> um das eine Raetsel zu spielen." + h.tail
  resp = make_response(html)
  resp.set_cookie('game', gl.number_to_cookie([int(id), 0])[1])
  resp.set_cookie('ts', str(int( time.time() )))
  return resp

@app.route('/deactivateRiddle')
def deactivateRiddle():
  #Check session
  conn, c = db.connect()
  if not(gl.checkSession(request, c)):
    db.close(conn)
    return h.head + "Session does not match. Back to <a href=\"/admin\">Login</a>." + h.tail
  
  sql = "select id, title, active from riddle"
  c.execute(sql)
  result = c.fetchall()
  
  status = ("Off", "On")
  html = []
  html.append("<p>Wähle Rätsel aus (ID), welches du switchen möchtest. Zum <a href=\"/adminPanel\">Admin-Panel</a>.</p>\n")
  html.append("<table>\n")
  html.append("<tr><th>ID</th><th>Titel</th><th>Status</th></tr>\n")
  for i in result:
    html.append("<tr><td><a href=\"doDeactivateRiddle/"+ str(i[0]) +"\">"+ str(i[0]) +"</a></td><td>"+ i[1] +"</td><td>"+ status[i[2]] +"</td></tr>\n")
  html.append("</table>")    

  db.close(conn)
  return h.head + ''.join(html) + h.tail

@app.route('/doDeactivateRiddle/<id>')
def doDeactivateRiddle(id):
  nr = gl.filter_only_numbers(id)
  if len(nr) == 0:
    return "ID wrong."
  
  #Check session
  conn, c = db.connect()
  if not(gl.checkSession(request, c)):
    db.close(conn)
    return h.head + "Session does not match. Back to <a href=\"/admin\">Login</a>." + h.tail

  sql = "select active from riddle where id = %s"
  c.execute(sql, [nr])
  r = c.fetchone()[0]
  if (r == 0):
    r = 1
  else:
    r = 0
  sql = "update riddle set active = %s where id = %s"
  c.execute(sql, [r, nr])
  conn.commit()
  db.close(conn)

  return h.head + "Riddle activation switched. Back to <a href=\"/deactivateRiddle\">Riddle Status</a>." + h.tail

@app.route('/adminDeleteRiddle/<id>')
def adminDeleteRiddle(id):
  nr = gl.filter_only_numbers(id)
  if len(nr) == 0:
    return "ID wrong."

  #Check session
  conn, c = db.connect()
  if not(gl.checkSession(request, c)):
    db.close(conn)
    return h.head + "Session does not match. Back to <a href=\"/admin\">Login</a>." + h.tail
  

  # Check if user did really approve deletation
  y = request.args.get('y', '')
  if (y == "y"):
    sql = "delete from riddle where id = %s"
    c.execute(sql, [nr])
    conn.commit()
    db.close(conn)
    return h.head + "<p>Rätsel "+nr+" gelöscht. </p><p>Zurück zum <a href=\"/adminPanel\">Admin Panel</a>.</p>" + h.tail
  else:
    db.close(conn)
    return h.head + "<p>Willst du wirklich Rätsel Nr. "+ nr +" löschen? Wenn ja, <a href=\"/adminDeleteRiddle/"+ nr +"?y=y\">KLICK MICH</a>.</p><p>Zurück zum <a href=\"/adminPanel\">Admin Panel</a>.</p>" + h.tail


@app.route('/pictures')
def pictures():
  #Check session
  conn, c = db.connect()
  if not(gl.checkSession(request, c)):
    db.close(conn)
    return h.head + "Session does not match. Back to <a href=\"/admin\">Login</a>." + h.tail
  db.close(conn)

  #l = getcwd()
  #return l

  l = listdir(path=pic_path)
  
  html = []
  html.append("<p>Go back to <a href=\"/adminPanel\">Admin Panel</a>.</p>\n")
  html.append("<table>\n")
  #html.append("<tr><td>Delete</td><td>Picture name</td></tr>\n")
  for i in l:
    link = '<a href="static/img/riddle/'+ i +'">'+ i +'</a>'
    html.append("<tr>\n\t<td>"+ link +"</td>\n\t<td><a href=\"/pictureDelete/"+i+"\">Delete</a></td>\n</tr>\n")
  html.append("</table>\n")
  return h.head + "".join(html) + h.tail


@app.route('/pictureDelete/<name>')
def pictureDelete(name):
  #Check session
  conn, c = db.connect()
  if not(gl.checkSession(request, c)):
    db.close(conn)
    return h.head + "Session does not match. Back to <a href=\"/admin\">Login</a>." + h.tail
  if not(gl.check_only_characters_and_underscore_and_point(name)):
    db.close(conn)
    return h.head + "For picture name only character like numbers, characters, point and underscore allowed." + h.tail
  db.close(conn)

  file1 = pic_path + name
  if ( exists(file1) ):
    remove(file1)
    return h.head + "Picture removed. Back to <a href=\"/pictures\">pictures</a>." + h.tail
  else:
    return h.head + "Picture not found. Back to <a href=\"/pictures\">pictures</a>." + h.tail


@app.route('/pictureUpload')
def pictureUpload():
  #Check session
  conn, c = db.connect()
  if not(gl.checkSession(request, c)):
    db.close(conn)
    return h.head + "Session does not match. Back to <a href=\"/admin\">Login</a>." + h.tail
  db.close(conn)

  html = []
  html.append("<p>Go back to <a href=\"/adminPanel\">Admin Panel</a>.</p>\n")

  html.append("<p>Falls das Bild zu groß ist, kann es eventuell nicht hochgeladen werden (Service-Beschränkung). Jedes Bild wird verkleinert, sofern es eine bestimmte Größe überschreitet.</p>\n")

  html.append('\n<form action="/doPictureUpload" method="post" enctype="multipart/form-data">\n')
  html.append('<input name="file1" type="file" size="25"><br />\n')
  #html.append('<input name="dir" type="hidden" value="'+ dir1 +'" size="25"><br />\n')
  html.append('<input type="submit" value="Upload" />\n')
  html.append('</form>\n\n')

  return h.head + ''.join(html) + h.tail


@app.route('/doPictureUpload', methods=['POST'])
def doPictureUpload():
  #Check session
  conn, c = db.connect()
  if not(gl.checkSession(request, c)):
    db.close(conn)
    return h.head + "Session does not match. Back to <a href=\"/admin\">Login</a>." + h.tail
  db.close(conn)

  html = []
  html.append("<p>Go back to <a href=\"/adminPanel\">Admin Panel</a>.</p>\n")

  f = request.files["file1"]
  filename = f.filename

  if not(gl.check_only_characters_and_underscore_and_point(filename)):
    return h.head + "For picture name only character like numbers, characters, point and underscore allowed. <p>Go back to <a href=\"/pictures\">pictures</a>.</p>" + h.tail

  ending = filename.split('.')
  try:
    ending = ending[1]
  except:
    return "No point in filename"
  if (ending.capitalize()[0]) == 'J':
    ending = 'JPEG'
  elif (ending.capitalize()[0]) == 'P':
    ending = 'PNG'
  else:
    return "Only JPG or PNG Files allowed."
  
  filename = pic_path + filename

  if ( exists(filename) ):
    remove(filename)
  f.save(filename)

  # Make picture smaller if too big
  im = Image.open(filename)
  (width1, height1) = im.size
  result = "File uploaded."
  if (width1 > 1000 or height1 > 1000):
    if width1 >= height1:
      width2 = gl.max_pic_size
      height2 = height1/width1*width2
    else:
      height2 = gl.max_pic_size
      width2 = width1/height1*height2
    #
    (width2, height2) = (int(width2), int(height2))
    im = im.resize((width2, height2))
    #
    #
    try:
      im.save(filename, ending)
      #print(filename, ': ', width1, height1, ' > ', width2, height2)
      result = "File uploaded. Image has been reduced in size."
    except:
      #print(filename, ' nicht gespeichert.')
      result = "File uploaded not uploaded. Problems while saving"
    #
  html.append('<p>'+ result +'</p>\n')
  html.append("<p>Go to <a href=\"/pictures\">pictures</a>.</p>\n")

  return h.head + ''.join(html) + h.tail

@app.route('/editCode')
def editCode():
  #Check session
  conn, c = db.connect()
  if not(gl.checkSession(request, c)):
    db.close(conn)
    return h.head + "Session does not match. Back to <a href=\"/admin\">Login</a>." + h.tail

  html = []

  sql = "select code from riddle limit 1"
  c.execute(sql)
  result = c.fetchone()

  html.append("<p>Current Code: <b>"+ result[0] +"</b></p>\n")

  html.append("<form action=\"/doEditCode\" method=\"post\">New Code:<br>\n<input type=\"code\" name=\"code\"><br>\n<input type=\"submit\" value=\"Abschicken\">\n</form>\n\n")

  html.append("<p>&nbsp;</p><p>Go back to <a href=\"/adminPanel\">Admin Panel</a>.</p>\n")

  db.close(conn)
  return h.head + ''.join(html) + h.tail

@app.route('/doEditCode', methods=['POST'])
def doEditCode():
  #Check session
  conn, c = db.connect()
  if not(gl.checkSession(request, c)):
    db.close(conn)
    return h.head + "Session does not match. Back to <a href=\"/admin\">Login</a>." + h.tail

  code = request.form.get("code")  

  if not(gl.check_only_characters_and_nr(code)):
    db.close(conn)
    return h.head + "Nur Buchstaben und Nummern erlaubt. Back to <a href=\"/editCode\">editCode</a>." + h.tail

  sql = "update riddle set code = %s"
  c.execute(sql, [code])
  conn.commit()

  db.close(conn)
  return h.head + "<p>Code wurde auf <b>"+code+"</b> geändert.</p><p>Back to <a href=\"/adminPanel\">adminPanel</a>.</p>\n"


@app.route('/editDelay')
def editDelay():
  #Check session
  conn, c = db.connect()
  if not(gl.checkSession(request, c)):
    db.close(conn)
    return h.head + "Session does not match. Back to <a href=\"/admin\">Login</a>." + h.tail

  html = []

  sql = "select delay from riddle limit 1"
  c.execute(sql)
  result = c.fetchone()

  html.append("<p>Current Time: <b>"+ str(result[0]) +"</b> Sekunden</p>\n")

  html.append("<form action=\"/doEditDelay\" method=\"post\">New Delay:<br>\n<input type=\"delay\" name=\"delay\"><br>\n<input type=\"submit\" value=\"Abschicken\">\n</form>\n\n")

  html.append("<p>&nbsp;</p><p>Go back to <a href=\"/adminPanel\">Admin Panel</a>.</p>\n")

  db.close(conn)
  return h.head + ''.join(html) + h.tail

@app.route('/doEditDelay', methods=['POST'])
def doEditDelay():
  #Check session
  conn, c = db.connect()
  if not(gl.checkSession(request, c)):
    db.close(conn)
    return h.head + "Session does not match. Back to <a href=\"/admin\">Login</a>." + h.tail

  delay = request.form.get("delay")  
  if len(delay) == 0:
    db.close(conn)
    return "Keine Angabe"

  if not(gl.check_only_numbers(delay)):
    db.close(conn)
    return h.head + "Nur Nummern erlaubt. Back to <a href=\"/editDelay\">editDelay</a>." + h.tail

  sql = "update riddle set delay = %s"
  c.execute(sql, [delay])
  conn.commit()

  db.close(conn)
  return h.head + "<p>Delay wurde auf <b>"+delay+"</b> geändert.</p><p>Back to <a href=\"/adminPanel\">adminPanel</a>.</p>\n"


@app.route('/newRiddle')
def newRiddle():
  #Check session
  conn, c = db.connect()
  if not(gl.checkSession(request, c)):
    db.close(conn)
    return h.head + "Session does not match. Back to <a href=\"/admin\">Login</a>." + h.tail
  db.close(conn)

  html = []
  html.append("<p>Back to <a href=\"/adminPanel\">adminPanel</a>.</p>\n")

  html.append("<form action=\"/doNewRiddle\" method=\"post\">\n")
  html.append("<p>Titel für das neue Rätsel<br>\n")
  html.append("<input name=\"title\" type=\"text\" autocomplete=\"off\" style=\"width:100px\"></p>\n")
  html.append("<p>Adresse<br>\n")
  html.append("<input name=\"address\" type=\"text\" autocomplete=\"off\" style=\"width:100px\"></p>\n")
  html.append("<p>Name des Karten-Bildes<br>\n")
  html.append("<input name=\"map\" type=\"text\" autocomplete=\"off\" style=\"width:100px\"></p>\n")
  html.append("<p>Name des Bildes der Umgebung<br>\n")
  html.append("<input name=\"pic\" type=\"text\" autocomplete=\"off\" style=\"width:100px\"></p>\n")
  html.append("<p>Rätsel Text<br>\n")
  html.append("<textarea name=\"riddleText\"></textarea></p>\n") #rows=\"6\" cols=\"50\"
  html.append("<p>Rätsel Antwort (Kleinbuchstaben und Zahlen)<br>\n")
  html.append("<input name=\"answer\" type=\"text\" autocomplete=\"off\" style=\"width:100px\"></p>\n")
  html.append("<p><input type=\"submit\" value=\"Abschicken\"></p>\n")
  html.append("</form>\n")

  return h.head + ''.join(html) + h.tail

@app.route('/doNewRiddle', methods=['POST'])
def doNewRiddle():
  #Check session
  conn, c = db.connect()
  if not(gl.checkSession(request, c)):
    db.close(conn)
    return h.head + "Session does not match. Back to <a href=\"/admin\">Login</a>." + h.tail

  title = request.form.get("title")
  address = request.form.get("address")
  map = request.form.get("map")
  pic = request.form.get("pic")
  riddleText = request.form.get("riddleText")
  answer = request.form.get("answer")

  title = gl.filter_only_characters_and_nr_and_space(title)
  if len(title) == 0:
    db.close(conn)
    return "Kein Titel angegeben. Gehe zurueck mit dem Browser."
  
  address = gl.filter_only_characters_and_nr_and_space(address)
  map = gl.filter_only_characters_and_nr_and_point(map)
  pic = gl.filter_only_characters_and_nr_and_point(pic)
  riddleText = gl.filter_bad_chars(riddleText)
  riddleText = riddleText.replace("\n", "<br>")
  answer = gl.filter_only_small_characters_and_numbers(answer)
  if len(title) == 0:
    db.close(conn)
    return "Keine Lsg. angegeben. Gehe zurueck mit dem Browser."

  sql = "select id from riddle"
  c.execute(sql)
  result = c.fetchall()

  # Create set out of result
  lst1 = []
  set1 = set(list(range(0,26)))
  for i in result:
    lst1.append(i[0])
  set2 = set(lst1)
  set3 = set1 - set2

  print(set1, set2, set3)

  if len(set3) == 0:
    db.close(conn)
    return "Kein Platz mehr fuer weitere Raetsel."

  nextId = set3.pop()
  
  sql = "INSERT INTO riddle(id, title, address, map, picture, text1, active, delay, answer, code) VALUES(%s, %s, %s, %s, %s, %s, 1, %s, %s, %s)"
  
  new_riddle = (nextId, title, address, map, pic, riddleText, gl.delay1, answer, gl.codeword)
  c.execute(sql, new_riddle)
  conn.commit()

  db.close(conn)
  return h.head + "Riddle added. <a href=\"/adminPanelChooseRiddle\">Go back to Riddles</a>." + h.tail


@app.route('/adminLogout')
def adminLogout():
  resp = make_response(h.head + "Logout erfolgt. Zurück zur <a href=\"/\">Hauptseite</a>." + h.tail)

  # Delete Cookie and empty session in DB
  resp.delete_cookie('session')
  
  conn, c = db.connect()
  sql = "update other set session = '' where id=1"
  c.execute(sql)
  conn.commit()
  db.close(conn)

  return resp

@app.route('/reset')
def reset():
  html = []
  html.append("<h4>Reset alles Rätsel</h4>\n")
  html.append("<p>Achtung: Bei Eingabe des richtigen Passwortes wird die aktuelle Datenbank (falls vorhanden) komplett mit der Standard Rätsel Datenbank überschrieben.</p>\n")
  html.append("<p>&nbsp;</p>\n")
  html.append("<form action=\"/resetPost\" method=\"post\">Passwort:<br>\n<input type=\"password\" name=\"password\"><br>\n<input type=\"submit\" value=\"Abschicken\">\n</form>")

  return h.head + "".join(html) + h.tail


@app.route('/resetPost', methods=['POST'])
def resetPost():

  pwHash = request.form.get("password").encode('utf-8')
  pwHash = hashlib.sha256(pwHash).hexdigest()

  if pwHash == gl.pw1:
    conn, c = db.connect()
    c.execute("DROP TABLE IF EXISTS riddle")
    c.execute(gl.riddle_table)
    c.execute("DROP TABLE IF EXISTS other")
    c.execute(gl.other_table)
    conn.commit()

    sql = "INSERT INTO riddle(id, title, address, map, picture, text1, active, delay, answer, code) VALUES(%s, %s, %s, %s, %s, %s, 1, %s, %s, %s)"
    c.executemany(sql, gl.riddle)
      #for i in gl.riddle:
      #  print(i)
      #  c.execute(sql, i)
    conn.commit()

    sql = "INSERT INTO other(id, session) VALUES(1, '')"
    c.execute(sql)
    conn.commit()

    db.close(conn)
    return "Table deleted and created."
  else:
    return "Wrong password"
