"""Calendar API routes."""
import os
import pickle
from datetime import datetime, timedelta, date
from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException, Request
import schemas
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import Flow

router = APIRouter(prefix="/api/calendar", tags=["calendar"])

# Global variables for Google Calendar service
calendar_service = None
calendar_id = None

def init_google_calendar():
    """Initialize Google Calendar service if credentials are available."""
    global calendar_service, calendar_id

    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    calendar_id_env = os.getenv('GOOGLE_CALENDAR_ID', 'primary')

    if not client_id or not client_secret:
        print("Google Calendar: Missing GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET")
        return False

    try:
        # For now, we'll use a simple token storage approach
        # In production, you'd want to use a proper database or secure storage
        token_file = '/app/google_token.pickle'

        creds = None
        if os.path.exists(token_file):
            with open(token_file, 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(GoogleRequest())
            else:
                # This would require OAuth flow - for now, return False
                print("Google Calendar: No valid credentials found. Need OAuth setup.")
                return False

            # Save the credentials for the next run
            with open(token_file, 'wb') as token:
                pickle.dump(creds, token)

        calendar_service = build('calendar', 'v3', credentials=creds)
        calendar_id = calendar_id_env
        print(f"Google Calendar: Initialized with calendar ID: {calendar_id}")
        return True

    except Exception as e:
        print(f"Google Calendar: Failed to initialize: {e}")
        return False

def get_google_calendar_events(target_date: date) -> List[schemas.CalendarEvent]:
    """Fetch events from Google Calendar."""
    if not calendar_service or not calendar_id:
        return []

    try:
        # Get events from target_date to target_date + 7 days
        start_datetime = datetime.combine(target_date, datetime.min.time())
        end_datetime = start_datetime + timedelta(days=7)

        events_result = calendar_service.events().list(
            calendarId=calendar_id,
            timeMin=start_datetime.isoformat() + 'Z',
            timeMax=end_datetime.isoformat() + 'Z',
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = []
        for event in events_result.get('items', []):
            # Parse start and end times
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))

            # Convert to datetime objects
            start_dt = datetime.fromisoformat(start.replace('Z', '+00:00')) if 'T' in start else datetime.combine(
                date.fromisoformat(start), datetime.min.time()
            )
            end_dt = datetime.fromisoformat(end.replace('Z', '+00:00')) if 'T' in end else datetime.combine(
                date.fromisoformat(end), datetime.min.time()
            )

            events.append(schemas.CalendarEvent(
                id=event['id'],
                title=event.get('summary', 'Untitled Event'),
                start=start_dt,
                end=end_dt,
                description=event.get('description'),
                location=event.get('location')
            ))

        return events

    except HttpError as e:
        print(f"Google Calendar API error: {e}")
        return []
    except Exception as e:
        print(f"Error fetching Google Calendar events: {e}")
        return []


def get_mock_events() -> List[schemas.CalendarEvent]:
    """
    Return mock calendar events as fallback when Google Calendar is not available.
    """
    today = datetime.utcnow()

    return [
        schemas.CalendarEvent(
            id="mock-1",
            title="Team Meeting",
            start=today.replace(hour=10, minute=0, second=0, microsecond=0),
            end=today.replace(hour=11, minute=0, second=0, microsecond=0),
            description="Weekly sync with the team",
            location="Conference Room A",
        ),
        schemas.CalendarEvent(
            id="mock-2",
            title="Lunch",
            start=today.replace(hour=12, minute=0, second=0, microsecond=0),
            end=today.replace(hour=13, minute=0, second=0, microsecond=0),
            description="Team lunch",
        ),
        schemas.CalendarEvent(
            id="mock-3",
            title="Project Review",
            start=(today + timedelta(days=1)).replace(hour=14, minute=0, second=0, microsecond=0),
            end=(today + timedelta(days=1)).replace(hour=15, minute=30, second=0, microsecond=0),
            description="Quarterly project review",
            location="Virtual - Zoom",
        ),
    ]


@router.get("/events", response_model=schemas.CalendarEventsResponse)
def get_calendar_events(date_param: date = Query(None)):
    """
    Get calendar events for a specific date (or today if not specified).
    Returns upcoming events from that date onwards.
    """
    if date_param is None:
        date_param = datetime.utcnow().date()

    # Try to get real Google Calendar events first
    if os.getenv('GOOGLE_CALENDAR_ENABLED', 'false').lower() == 'true':
        if calendar_service is None:
            init_google_calendar()

        if calendar_service:
            events = get_google_calendar_events(date_param)
            if events:  # If we got events from Google Calendar, return them
                return schemas.CalendarEventsResponse(
                    events=events,
                    date=date_param,
                )

    # Fall back to mock events if Google Calendar is not available or failed
    events = get_mock_events()

    # Filter events to those on or after the specified date
    filtered_events = [
        event for event in events
        if event.start.date() >= date_param
    ]

    return schemas.CalendarEventsResponse(
        events=filtered_events,
        date=date_param,
    )


@router.get("/auth/google")
def google_auth():
    """Initiate Google OAuth flow."""
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    redirect_uri = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:8000/auth/google/callback')

    if not client_id or not client_secret:
        raise HTTPException(status_code=500, detail="Google Calendar credentials not configured")

    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uris": [redirect_uri],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=['https://www.googleapis.com/auth/calendar.readonly'],
        redirect_uri=redirect_uri
    )

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )

    # Store state for verification (in production, use secure storage)
    with open('/tmp/google_auth_state.txt', 'w') as f:
        f.write(state)

    return {"authorization_url": authorization_url}


@router.get("/auth/google/callback")
def google_auth_callback(code: str, state: str):
    """Handle Google OAuth callback."""
    try:
        # Verify state
        with open('/tmp/google_auth_state.txt', 'r') as f:
            stored_state = f.read().strip()

        if state != stored_state:
            raise HTTPException(status_code=400, detail="Invalid state parameter")

        client_id = os.getenv('GOOGLE_CLIENT_ID')
        client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        redirect_uri = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:8000/auth/google/callback')

        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "redirect_uris": [redirect_uri],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=['https://www.googleapis.com/auth/calendar.readonly'],
            redirect_uri=redirect_uri
        )

        flow.fetch_token(code=code)

        # Save credentials
        creds = flow.credentials
        with open('/app/google_token.pickle', 'wb') as token:
            pickle.dump(creds, token)

        # Initialize calendar service
        global calendar_service, calendar_id
        calendar_service = build('calendar', 'v3', credentials=creds)
        calendar_id = os.getenv('GOOGLE_CALENDAR_ID', 'primary')

        return {"message": "Google Calendar authentication successful"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")
