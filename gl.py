#!/usr/bin/python3


# HTML
#https://unpkg.com/sakura.css/css/sakura.css

# FUNCTIONS

# https://www.geeksforgeeks.org/flask-cookies/

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

def filter_only_characters(str1):
  str2 = []
  for i in str1:
    nr = ord(i)
    if (nr >= 65 and nr <= 90) or (nr >= 97 and nr <= 122):
      str2.append(i)
  return "".join(str2)

def filter_only_characters_and_nr(str1):
  str2 = []
  for i in str1:
    nr = ord(i)
    if (nr >= 48 and nr <= 57) or (nr >= 65 and nr <= 90) or (nr >= 97 and nr <= 122):
      str2.append(i)
  return "".join(str2)


def check_only_characters_and_underscore_and_point(str1):
  str2 = []
  for i in str1:
    nr = ord(i)
    if not(nr >= 48 and nr <= 57) and not(nr >= 65 and nr <= 90) and not(nr >= 97 and nr <= 122) and nr != 95 and nr != 46:
      return False
  return True


def filter_bad_sql(str1):
  # "=34 &=38 '=39 *=42 /=47 ;=59 <=60 >=62
  # "/" vorerst erlaubt wegen Links
  str2 = []
  for i in str1:
    nr = ord(i)
    if nr in (34, 38, 39, 42, 59, 60, 62) or nr in range(0, 10) or nr in range(11, 31):
      pass
    else:
      str2.append(i)
  return "".join(str2)

def render_riddle(str1):
  str1 = str1.replace("\n", "<br>\n")
  return str1

def cookie_to_number(str1):
  list1 = []
  for i in str1:
    nr = ord(i)
    if (nr >= 65 and nr <= 90):
      list1.append(nr-64) #1-26
    elif (nr >= 97 and nr <= 122):
      list1.append(nr-70) #27-52
    else:
      pass
  
  if len(list1) == 0:
    return False, 0
  else:
    return True, list1

def number_to_cookie(list1):
  list2 = []
  for i in list1:
    if (i >= 1 and i <= 26): #A-Z
      list2.append(chr(64+i))
    elif (i >= 27 and i <= 52):
      list2.append(chr(70+i)) #a-z

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