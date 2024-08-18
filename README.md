Google Calendar Time Tracker App
================================

Introduction
------------

The Google Calendar Time Tracker app is designed to simplify the management of events in your Google Calendar using natural language commands. This app allows you to add, update, reschedule, and delete events with ease, directly integrating with your Google Calendar.

Features
--------

-   **Natural Language Processing (NLP):** Interact with your calendar using simple, conversational commands.

-   **Add Events:** Quickly create new events with a specified duration and title.

-   **Update Events:** Modify the duration of existing events.

-   **Reschedule Events:** Move events forward or backward in time.

-   **Delete Events:** Remove events that are no longer needed.

Prerequisites
-------------

Before you begin, ensure you have the following installed:

-   Python 3.7 or higher

-   Pip (Python package installer)

-   Google Cloud Project with OAuth 2.0 credentials

Setup Instructions
------------------

### 1\. Clone the Repository

Clone the project repository to your local machine:

```
git clone https://github.com/your-username/google-calendar-time-tracker.git

cd google-calendar-time-tracker
```

### 2\. Set Up a Virtual Environment

It's recommended to use a virtual environment to manage dependencies:

```
python -m venv venv

source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3\. Install Dependencies

Install the required Python packages:


```
pip install -r requirements.txt
```

### 4\. Configure Google Cloud OAuth 2.0

1.  Go to the Google Cloud Console.

2.  Create a new project (if you don't already have one).

3.  Navigate to APIs & Services > Credentials.

4.  Create OAuth 2.0 credentials and download the credentials.json file.

5.  Place the credentials.json file in the root directory of the project.

### 5\. Set Up Environment Variables

Ensure the following environment variables are set:

-   OAUTHLIB_INSECURE_TRANSPORT: Set this to 1 to allow OAuth 2.0 to work on http://localhost.

-   FLASK_APP: Set this to app.py.

### 6\. Run the Application

Start the Flask application:

```
python app.py
```

The app should now be running on http://localhost:5000.

### 7\. Authenticate with Google

1.  Open your web browser and go to http://localhost:5000/login.

2.  Authenticate with your Google account to allow the app to access your Google Calendar.

3.  Once authenticated, you can start using the app.

Usage Instructions
------------------

You can interact with the app via HTTP POST requests to the /process_command endpoint. Use a tool like Postman to send JSON commands.

### Example Commands

-   Add an event:

```json
{
    "command": "add 30 minutes to 'Team Meeting'"
}
```

-   Update an event:

```json
{

    "command": "update 'Budget Review' by 15 minutes"

}
```

-   Reschedule an event:

```json
{

    "command": "reschedule 'Project Kickoff' by 30 minutes"

}
```

-   Delete an event:

```json

{

    "command": "delete 'Weekly Standup'"

}

```

Troubleshooting
---------------

### Common Issues

-   **Invalid Credentials:** Ensure that the credentials.json file is correctly placed and contains valid OAuth 2.0 credentials.

-   **Environment Variables:** Double-check that all required environment variables are set correctly.

-   **Authentication Issues:** If you're having trouble authenticating, clear your browser's cache and cookies, then try logging in again.

### Logging and Debugging

To enable debug mode in Flask, run the application with the --debug flag:

```
python app.py --debug
```

Deployment
----------

For deployment to a production environment, consider using a WSGI server like Gunicorn and setting up HTTPS.


Contact
-------

For any questions or support, please contact:

-   Developer: Hamza Ahmad

-   Email: hamzaahmad277@gmail.com
