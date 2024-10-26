head = '''<!DOCTYPE html>
<html lang="de">

<head>
<title>Riddle</title>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="static/sakura.css" type="text/css">
</head>
<body>

<h1>Mosbach Riddle</h1>
'''


tail = '''
</body>
</html>
'''


def render_riddle(str1):
  str1 = str1.replace("\n", "<br>\n")
  return str1


def template_start(address, map, picture, content):
  lst1 = []
  lst1.append('<p>Adresse: '+address+'</p>\n')
  lst1.append('<p><a href="static/img/riddle/'+map+'"><img src="static/img/riddle/'+map+'" alt="Karte" width="300"></a></p>\n')
  lst1.append('<p><a href="static/img/riddle/'+picture+'"><img src="static/img/riddle/'+picture+'" alt="Bild von Rätsel" width="300"></a></p>\n')
  lst1.append(content + "\n")
  return ''.join(lst1)


def template_riddle(id, title, address, map, picture, content, current, max, answer):
  lst1 = []
  # Optional
  # lst1.append('<p>'+status+'</p>')
  lst1.append('<p></p>\n')
  lst1.append('Rätsel '+str(current)+' von ' +str(max))
  lst1.append('<form action="/beenden" method="get"><input type="submit" value="Spiel abbrechen"></form>\n')
  lst1.append('<h3>'+title+'</h3>\n')
  lst1.append(template_start(address, map, picture, content))

  lst1.append('<form action="/checkAnswer" method="get">\n')
  lst1.append('<input type="hidden" name="id" value="'+str(id)+'">\n')
  lst1.append('<input type="text" name="answer" autocomplete="off"><br>\n')
  lst1.append('<input type="submit" value="Abschicken">\n')
  lst1.append('</form>\n\n')

  lst1.append('<p>(Antwort: '+answer+')</p>\n')

  return ''.join(lst1)

