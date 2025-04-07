#!/usr/bin/python3

# CONSTANTS
# 0 = online on Pythonanywhere, 1 = local for your computer. It changes directories for upload and DB settings
local1 = 1
pw1 = "" # Password for admin panel and reset button ( import hashlib, a="password".encode('utf-8'), pw1=hashlib.sha256(a).hexdigest() )

#max_riddle = 5 # Not used right now, as all riddles need to be solved
max_pic_size = 500

# DATABASES GLOBALS

# auto_increment
# delay = Zeitdifferenz, die man warten muss, bis mehr Infos angezeigt werden
# answer = Antwort auf das Raetsel
riddle_table = """CREATE TABLE riddle(
id INTEGER NOT NULL,
title VARCHAR(50),
address VARCHAR(50),
map VARCHAR(40),
picture VARCHAR(40),
text1 TEXT,
active INTEGER,
delay INTEGER,
answer VARCHAR(20),
code VARCHAR(20),
PRIMARY KEY (id))"""

other_table = """CREATE TABLE other(
id INTEGER NOT NULL,
session VARCHAR(50))
"""

#select count(*) from riddle;
codeword = "Newton"
delay1 = 60
riddle = [
  (0, 'Badgasse', 'Badgasse 1', 'badgasse_karte.png', 'badgasse.jpg', 'Wie lautet die Jahreszahl unter dem Degerdon Schriftzug?', delay1, '1846', codeword),
  (1, 'Kiwwel Schisser', 'Badgasse 10', 'kiwwel_schisser_map.png', 'kiwwel_schisser.jpg', 'In welchem Jahr wurde der Brunnen von der Stadt Mosbach errichtet? Schau dazu die Tafel rechts davon an.', delay1, '1987', codeword),
  (2, 'Karusell', 'Hauptstr. 5', 'karusell_karte.png', 'karusell.jpg', 'Wie viele Schaukeln befinden sich an dem Karusell?', delay1, '6', codeword),
  (3, 'Kandelschussbrunnen', 'Schlossgasse / Heugasse', 'kandelschussbrunnen_map.png', 'kandelschussbrunnen.jpg', 'Wie viele Stufen befinden sich auf dem Weg nach oben?', delay1, '45', codeword),
  (4, 'Kesslergasse', 'Kesslergasse', 'kesslergasse_karte.png', 'kesslergasse.jpg', 'Wie viele Gullideckel (eckig und rund) befinden sich auf der unsichtlich gemachten Straße?', delay1, '5', codeword),
  (5, 'Pippig Uhr', 'Schmelzweg', 'pippigUhr_karte.png', 'pippig_uhr.jpg', 'Um was für einen Typ Anzeige handelt es sich bei der untersten Uhr? Lösung als Kleinbuchstaben eingeben.', delay1, 'hygrometer', codeword),
  (6, 'Stadtverwaltung', 'In der Nähe vom Marktplatz', 'stadtverwaltung_karte.png', 'stadtverwaltung.jpg', 'Wie viele Stufen befinden sich auf dem Weg nach oben (rechte Seite)?<br>Zähle die unteren, kleinen Stufen mit.', delay1, '30', codeword)
  ]







# FUNCTION GLOBALS

def checkSession(request, c):
  sql = "select session from other where id=1"
  c.execute(sql)
  result = c.fetchone()[0]
  if (request.cookies.get('session') == result):
    return True
  return False

  

# Gibt timestamp zurueck, geht darum erst nach einer bestimmten Zeit etwas anzeigen zu lassen
def read_ts_cookie(request):
  ts = request.cookies.get('ts')
  if ts == None:
    return False, 0
  ts = filter_only_numbers(ts)
  if len(ts) < 10:
    return False, 0
  return True, int(ts)

# Gibt gutes zurueck wenn Spiel gerade laeuft (True und Spielstand)
def read_cookie(request):
  game = request.cookies.get('game')
  if game == None:
    return False, []
  game = filter_only_characters(game)
  if len(game) < 2:
    return False, []
  return cookie_to_number(game)


def filter_only_numbers(str1):
  str2 = []
  for i in str1:
    nr = ord(i)
    if (nr >= 48 and nr <= 57):
      str2.append(i)
  return "".join(str2)

def check_only_numbers(str1):
  for i in str1:
    nr = ord(i)
    if (nr < 48 or nr > 57):
      return False
  return True


def filter_only_characters(str1):
  str2 = []
  for i in str1:
    nr = ord(i)
    if (nr >= 65 and nr <= 90) or (nr >= 97 and nr <= 122):
      str2.append(i)
  return "".join(str2)

def filter_only_small_characters(str1):
  str2 = []
  for i in str1:
    nr = ord(i)
    if (nr >= 97 and nr <= 122):
      str2.append(i)
  return "".join(str2)

def filter_only_small_characters_and_numbers(str1):
  str2 = []
  for i in str1:
    nr = ord(i)
    if (nr >= 48 and nr <= 57) or (nr >= 97 and nr <= 122):
      str2.append(i)
  return "".join(str2)

def filter_only_characters_and_nr(str1):
  str2 = []
  for i in str1:
    nr = ord(i)
    if (nr >= 48 and nr <= 57) or (nr >= 65 and nr <= 90) or (nr >= 97 and nr <= 122):
      str2.append(i)
  return "".join(str2)

def filter_only_characters_and_nr_and_point(str1):
  str2 = []
  for i in str1:
    nr = ord(i)
    if (nr >= 48 and nr <= 57) or (nr >= 65 and nr <= 90) or (nr >= 97 and nr <= 122) or nr == 46 or nr == 95:
      str2.append(i)
  return "".join(str2)

def filter_only_characters_and_nr_and_space(str1):
  str2 = []
  for i in str1:
    nr = ord(i)
    if (nr >= 48 and nr <= 57) or (nr >= 65 and nr <= 90) or (nr >= 97 and nr <= 122) or nr == 32:
      str2.append(i)
  return "".join(str2)

def check_only_characters_and_nr(str1):
  for i in str1:
    nr = ord(i)
    if not(nr >= 48 and nr <= 57) and not(nr >= 65 and nr <= 90) and not(nr >= 97 and nr <= 122):
      return False
  return True

def check_only_characters_and_underscore_and_point(str1):
  for i in str1:
    nr = ord(i)
    if not(nr >= 48 and nr <= 57) and not(nr >= 65 and nr <= 90) and not(nr >= 97 and nr <= 122) and nr != 95 and nr != 46:
      return False
  return True


def filter_bad_chars(str1):
  # html: <=60, >=62, &=38
  # "=34 &=38 '=39 *=42 /=47 ;=59 <=60 >=62 /=47
  str2 = []
  for i in str1:
    nr = ord(i)
    if nr in (34, 38, 39, 42, 47, 59, 60, 62) or nr in range(0, 10) or nr in range(11, 31):
      pass
    else:
      str2.append(i)
  return "".join(str2)

def cookie_to_number(str1):
  list1 = []
  for i in str1:
    nr = ord(i)
    if (nr >= 65 and nr <= 90):
      list1.append(nr-65) #0-25
    else:
      pass
  
  if len(list1) == 0:
    return False, 0
  else:
    return True, list1


def number_to_cookie(list1):
  list2 = []
  for i in list1:
    if (i >= 0 and i <= 25): #A-Z
      list2.append(chr(65+i))

  if len(list2) == 0:
    return False, ""
  else:
    return True, ''.join(list2)


def game2str(game):
  list1 = []
  for i in game:
    list1.append(str(i))
  return ', '.join(list1)

# For check: 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
