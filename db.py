import mysql.connector

def connect():
  conn = mysql.connector.connect(user='', password='', host='localhost', database='riddle')
  c = conn.cursor()
  return [conn, c]

def close(conn):
  conn.close()


# DATABASES GLOBALS

# auto_increment
# type1 = Textfeld oder Auswahl als Input
# answer = Antwort auf das Raetsel
riddle_table = """CREATE TABLE riddle(
id INTEGER NOT NULL,
title VARCHAR(50),
address VARCHAR(50),
map VARCHAR(40),
picture VARCHAR(40),
text1 TEXT,
active INTEGER,
type1 INTEGER,
answer VARCHAR(20),
code VARCHAR(20),
max INTEGER,
PRIMARY KEY (id))"""


riddle = [
  (1, 'Badgasse', 'Badgasse 1', '01_badgasse_karte.png', '01_badgasse.jpg', 'Wie lautet die Jahreszahl unter dem Degerdon Schriftzug?', '1846', 'Newton', 5),
  (2, 'Kiwwel Schisser', 'Badgasse 10', '02_brunnen_karte.png', '02_brunnen.jpg', 'In welchem Jahr wurde der Kiwwel Schisser von der Stadt Mosbach errichtet? Schau dazu die Tafel rechts davon an.', '1987', 'Newton', 5),
  (3, 'Karusell', 'Hauptstr. 5', '03_karusell_karte.png', '03_karusell.jpg', 'Wie viele Schaukeln befinden sich an dem Karusell?', '6', 'Newton', 5),
  (4, 'Schlossgasse', 'Schlossgasse / Heugasse', '04_schlossgasse_karte.png', '04_schlossgasse.jpg', 'Wie viele Stufen befinden sich auf dem Weg nach oben?', '45', 'Newton', 5),
  (5, 'Kesslergasse', 'Kesslergasse', '05_kesslergasse_karte.png', '05_kesslergasse.jpg', 'Wie viele Gullideckel (eckig und rund) befinden sich auf der unsichtlich gemachten Straße?', '5', 'Newton', 5),
  (6, 'Pippig Uhr', 'Schmelzweg', '06_pippigUhr_karte.png', '06_pippig_uhr.jpg', 'Um was für einen Typ Anzeige handelt es sich bei der untersten Uhr? Lösung als Kleinbuchstaben eingeben.', 'hygrometer', 'Newton', 5),
  (7, 'Stadtverwaltung', 'In der Nähe vom Marktplatz', '07_stadtverwaltung_karte.png', '07_stadtverwaltung.jpg', 'Wie viele Stufen befinden sich auf dem Weg nach oben (rechte Seite)?', '30', 'Newton', 5)
  ]
