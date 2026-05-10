# Google Calendar Setup Guide

## Prerequisites

1. **Google Cloud Console Account**: https://console.cloud.google.com/
2. **Google Calendar API Enabled**
3. **OAuth 2.0 Credentials**

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Google Calendar API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Calendar API"
   - Click "Enable"

## Step 2: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Configure OAuth consent screen if prompted:
   - User Type: External
   - App name: Digital Calendar
   - User support email: your-email@example.com
   - Developer contact: your-email@example.com
4. Application type: "Web application"
5. Authorized redirect URIs:
   - `http://localhost:8000/auth/google/callback` (for local development)
   - `http://100.104.202.19:8000/auth/google/callback` (for production)
6. Click "Create"
7. Save the Client ID and Client Secret

## Step 3: Get Your Calendar ID

1. Open Google Calendar in your browser
2. Click the settings gear > "Settings and sharing"
3. Find your shared family calendar in the list
4. Click on it and scroll down to "Calendar ID"
5. Copy the calendar ID (looks like: `xxxxx@group.calendar.google.com`)

## Step 4: Configure Environment Variables

Create a `.env` file in your project root:

```bash
# Copy from .env.example and fill in your values
cp .env.example .env

# Edit .env with your credentials:
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
GOOGLE_CALENDAR_ID=your_calendar_id@group.calendar.google.com
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback
```

## Step 5: Authenticate

1. Start your application: `docker compose up -d`
2. Visit: `http://localhost:8000/docs`
3. Go to `/api/calendar/auth/google` endpoint
4. Click "Try it out" > "Execute"
5. Open the `authorization_url` in your browser
6. Sign in with Google and grant calendar access
7. You'll be redirected back with success message

## Step 6: Test

Visit your dashboard at `http://localhost:3000` - the Calendar pane should now show real events from your shared Google Calendar!

## Troubleshooting

- **"Invalid client"**: Check your Client ID and Secret
- **"redirect_uri_mismatch"**: Ensure redirect URI matches exactly
- **"Access blocked"**: Make sure Calendar API is enabled
- **No events showing**: Check calendar sharing permissions

## Security Notes

- Never commit `.env` file to version control
- Use environment-specific credentials for production
- Regularly rotate OAuth credentials
- Consider using service accounts for server-to-server access (advanced)