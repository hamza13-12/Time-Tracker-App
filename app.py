from flask import Flask, redirect, url_for, session, request, jsonify
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import os
import datetime
from nlp_utils import parse_command  # Import the enhanced NLP function

app = Flask(__name__)
app.secret_key = 'YOUR_SECRET_KEY'
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Load credentials from file
SCOPES = ['https://www.googleapis.com/auth/calendar']
CLIENT_SECRETS_FILE = 'credentials.json'

@app.route('/')
def index():
    return 'Welcome to the Google Calendar Time Tracker!'

@app.route('/login')
def login():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)
    flow.redirect_uri = url_for('callback', _external=True)
    
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true')

    session['state'] = state
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    state = session['state']
    
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = url_for('callback', _external=True)

    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    session['credentials'] = credentials_to_dict(credentials)
    
    return redirect(url_for('projects'))

@app.route('/projects')
def projects():
    if 'credentials' not in session:
        return redirect('login')

    credentials = Credentials(**session['credentials'])
    service = build('calendar', 'v3', credentials=credentials)

    # Call the Calendar API to list events
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])
    
    projects = []
    for event in events:
        projects.append(event['summary'])

    return jsonify(projects)

@app.route('/process_command', methods=['POST'])
def process_command():
    if 'credentials' not in session:
        return redirect('login')

    # Get the command from the request body
    command = request.json.get('command')
    
    # Use the NLP utility function to parse the command
    intent, event_title, duration_minutes = parse_command(command)

    if not intent or not event_title:
        return jsonify({'status': 'Error', 'message': 'Could not parse the command.'})

    # Use the Calendar API to search for the existing event
    credentials = Credentials(**session['credentials'])
    service = build('calendar', 'v3', credentials=credentials)

    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time

    if intent == 'add':
        # Logic to add a new event
        return add_event(service, event_title, duration_minutes)

    elif intent == 'update':
        # Logic to update an existing event
        return update_event(service, event_title, duration_minutes, now)

    elif intent == 'delete':
        # Logic to delete an existing event
        return delete_event(service, event_title, now)

    elif intent == 'reschedule':
        # Logic to reschedule an existing event
        return reschedule_event(service, event_title, duration_minutes, now)

    return jsonify({'status': 'Error', 'message': 'Invalid intent.'})

def add_event(service, event_title, duration_minutes):
    now = datetime.datetime.utcnow()
    start_time = now.isoformat() + 'Z'
    end_time = (now + datetime.timedelta(minutes=duration_minutes)).isoformat() + 'Z'

    event = {
        'summary': event_title,
        'start': {
            'dateTime': start_time,
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'UTC',
        },
    }

    created_event = service.events().insert(calendarId='primary', body=event).execute()

    return jsonify({
        'status': 'Event created',
        'event_id': created_event.get('id'),
        'event_summary': created_event.get('summary')
    })

def update_event(service, event_title, duration_minutes, now):
    events_result = service.events().list(
        calendarId='primary',
        q=event_title,  # Search for the event by title
        timeMin=now,
        maxResults=10,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])

    if not events:
        return jsonify({'status': 'Error', 'message': f'No upcoming event found with title "{event_title}".'})

    event = events[0]
    end_time = datetime.datetime.fromisoformat(event['end']['dateTime'].replace('Z', ''))
    updated_end_time = (end_time + datetime.timedelta(minutes=duration_minutes)).isoformat()

    event['end']['dateTime'] = updated_end_time
    updated_event = service.events().patch(calendarId='primary', eventId=event['id'], body=event).execute()

    return jsonify({
        'status': 'Event updated',
        'event_id': updated_event.get('id'),
        'event_summary': updated_event.get('summary'),
        'new_end_time': updated_event['end']['dateTime']
    })

def delete_event(service, event_title, now):
    events_result = service.events().list(
        calendarId='primary',
        q=event_title,  # Search for the event by title
        timeMin=now,
        maxResults=10,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])

    if not events:
        return jsonify({'status': 'Error', 'message': f'No upcoming event found with title "{event_title}".'})

    event = events[0]
    service.events().delete(calendarId='primary', eventId=event['id']).execute()

    return jsonify({'status': 'Event deleted', 'event_id': event['id'], 'event_summary': event['summary']})

def reschedule_event(service, event_title, duration_minutes, now):
    events_result = service.events().list(
        calendarId='primary',
        q=event_title,  # Search for the event by title
        timeMin=now,
        maxResults=10,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])

    if not events:
        return jsonify({'status': 'Error', 'message': f'No upcoming event found with title "{event_title}".'})

    event = events[0]
    start_time = datetime.datetime.fromisoformat(event['start']['dateTime'].replace('Z', ''))
    new_start_time = start_time + datetime.timedelta(minutes=duration_minutes)
    new_end_time = new_start_time + (datetime.datetime.fromisoformat(event['end']['dateTime'].replace('Z', '')) - start_time)
    
    print(start_time)
    print(new_start_time)
    print(new_end_time)

    event['start']['dateTime'] = new_start_time.isoformat()
    event['end']['dateTime'] = new_end_time.isoformat() 

    updated_event = service.events().patch(calendarId='primary', eventId=event['id'], body=event).execute()

    return jsonify({
        'status': 'Event rescheduled',
        'event_id': updated_event.get('id'),
        'event_summary': updated_event.get('summary'),
        'new_start_time': updated_event['start']['dateTime'],
        'new_end_time': updated_event['end']['dateTime']
    })

def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}

if __name__ == '__main__':
    app.run('localhost', 5000, debug=True)
