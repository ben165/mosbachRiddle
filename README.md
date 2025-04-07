# Riddle Mosbach

Bei dieser Web Applikation handelt es sich um ein Spiel, dass Rätsel über die Stadt Mosbach enthält. Die Rätsel fragen Details über die Innenstadt. Es gibt eine kleine Admin Oberfläche zum Löschen, Bearbeiten, Einfügen von neuen Rätsel und ein paar Einstellungen.

Die Web Applikation ist momentan auf 
```
https://mosbachriddle.pythonanywhere.com/
```

gehostet.

## Lokale Installation

Als erstes clont man sich dieses Repo.

Dann erstellt man sich die virtuelle Umgebung und installiert die Abhänigkeiten:

```
python3 -m venv p3
```

Aktivierung

```
source p3/bin/activate
```

Installation der Pakete:

```
pip install -r requirements.txt
```

## Lokale Ausführung

Es eine eine MySQL oder MariaDB Datenbank nötig, mit der die Web-Applikation kommunizieren kann. Der Name der Datenbank (im unteren Beispiel `riddle`) muss händisch angelegt werden. Danach die Login Information in der Datei `db.py` in Zeile 4 anpassen. Als Beispiel kann das so aussehen:

```
conn = mysql.connector.connect(user='user1', password='user1', host='localhost', database='riddle')
```

Mit der Datenbank am Laufen kann die Applikation gestartet werden.

```
flask --app appfile.py --debug run
```

Der lokale Server wird gestartet

```
Running on http://127.0.0.1:5000
```

Um die ersten Rätsel in die Datenbank schreiben, folgende Route aufrufen (TODO: Diese Route danach entfernen. In der Online Version auf Pythonanywhere ist diese entfernt bzw. umbenannt):

```
http://127.0.0.1:5000/reset
```

Wenn alles geklappt hat, bekommt man als Response

```Table deleted and created.```

Jetzt kann man die Hauptseite aufrufen

```
http://127.0.0.1:5000/
```

und das Spiel spielen. Viel Spaß :)

## Installation auf Pythonanywhere

Die Installation auf Pythonanywhere ist in der Studienarbeit beschrieben. Sie unterscheided sich aber nicht stark von der lokalen Installation. Man muss halt die Datenbank Parameter in `db.py` entsprechend anpassen.

Eventuell wird die Studienarbeit selbst ebenfalls hier hochgeladen.