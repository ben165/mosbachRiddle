#!/usr/bin/bash

#export FLASK_APP=app_file
#export FLASK_ENV=development
#flask run

# New way of running a development server
#
# This doesnt work. Command "run" can't be found. User this instead:
#if __name__ == '__main__':
# app.run()
#
# in the program itself and run the program file.
#
#

#flask --app run app_file

# This one is working:
flask --app appfile.py --debug run


# Other way:
##echo "flask --app appfile.py --debug run"
#export FLASK_APP=appfile.py
#export FLASK_ENV=development
#flask run --host=0.0.0.0
#
