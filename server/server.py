from flask import Flask, request, render_template, send_from_directory

import attending
import database.database_create as db
import logins
import validation
from response import Response

db.get_usable_db()

app = Flask(__name__, template_folder='static', static_folder='static')


# Website index
@app.route('/')
def site_index():
    return render_template('index.html')


# Splash screen
@app.route('/splash')
def site_splash():
    return render_template('splash.html')


# Lecturer login
@app.route('/lecturer-login')
def site_lecturer_login():
    return render_template('lecturer-login.html')


# Lecturer webapp
@app.route('/lecturer-webapp')
def site_lecturer_webapp():
    return render_template('lecturer-webapp.html')


# Assets
@app.route('/static/<path:path>')
def get_assets(path):
    return send_from_directory(app.static_folder, path)


# Test endpoint for checking server is working
@app.route('/api/hello')
def hello():
    return 'hello'


# Endpoint called when student signs into their class
@app.route('/api/register-attendance', methods=['POST'])
def attend():
    student_id = request.form['user']
    event_uuid = request.form['event']
    if not student_id or not event_uuid:
        return Response('ValueError: SID or Event_id not found', 400)

    try:
        result, status = attending.register_student_attendance(student_id, event_uuid)
    except:
        result = {
            'message': 'A server error occurred'
        }
        status = 500

    return Response(result, status).send()


# Get student's attendance history
@app.route('/api/student-attendance-history', methods=['GET'])
def student_attendance():
    student_id = request.args.get('sid')

    try:
        student_id = validation.sid(student_id)
    except ValueError:
        return Response("Invalid Student ID", 400).send()

    return Response(attending.get_student_attendance(student_id)).send()


# Get event's attendance history
@app.route('/api/event-attendance-history', methods=['GET'])
def event_attendance():
    event_uuid = request.args.get('event')
    if not event_uuid:
        return Response("Invalid event ID", 400).send()
    return Response(attending.get_attendance_for_event(event_uuid)).send()


# Get lecturer's event history
# TODO: Methods like this need to be authenticated (lecturer can only get this info with valid login session)
@app.route('/api/lecturer-event-history', methods=['GET'])
def lecturer_events():
    lecturer_username = request.args.get('username')
    if not lecturer_username:
        return Response("Invalid lecturer username", 400).send()
    return Response(attending.get_events_by_lecturer(lecturer_username)).send()


# Get event's details
@app.route('/api/event-details', methods=['GET'])
def event_details():
    event_id = request.args.get('id')
    if not event_id:
        return Response("Invalid event ID", 400).send()
    try:
        event = attending.get_event(event_id)
    except:
        return Response("No such event", 404)
    return Response(event)


# Lecturer login
@app.route('/api/lecturer-login', methods=['POST'])
def lecturer_login():
    username = request.form['username']
    password = request.form['password']
    try:
        key = logins.lecturer_login(username, password)
    except ValueError:
        return Response("Password incorrect", 401).send()
    except:
        return Response("Server error", 500).send()
    # TODO: Return in JSON format - requires front-end (login) change
    return key


# Check login session is valid
@app.route('/api/lecturer-session-check', methods=['GET'])
def session_check():
    session_id = request.args.get('session')
    result = {
        'logged_in': logins.session_check(session_id)
    }
    return Response(result).send()


# Run server in debug mode, and auto restart on file change
if __name__ == "__main__":
    app.config.update(
        DEBUG=True,
        TEMPLATES_AUTO_RELOAD=True
    )
    app.run()
