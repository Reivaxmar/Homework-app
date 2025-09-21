# Authentication Setup Guide

This guide explains how to set up Supabase authentication with Google OAuth and Google Calendar integration for the Homework Management App.

## Prerequisites

1. A Supabase account (https://supabase.com)
2. A Google Cloud Console project (https://console.cloud.google.com)
3. Node.js and Python installed

## Step 1: Create Supabase Project

1. Go to [Supabase](https://supabase.com) and create a new project
2. Note down your:
   - Project URL (looks like: `https://your-project-id.supabase.co`)
   - Anon key (from Settings > API)
   - Service role key (from Settings > API)

## Step 2: Configure Google OAuth in Supabase

1. In your Supabase project, go to Authentication > Providers
2. Enable Google provider
3. You'll need to configure Google OAuth credentials (see Step 3)

## Step 3: Set up Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Google+ API
   - Google Calendar API
4. Go to "Credentials" and create OAuth 2.0 Client IDs
5. Configure the OAuth consent screen
6. Add authorized redirect URIs:
   - `https://your-project-id.supabase.co/auth/v1/callback`
   - `http://localhost:3000/auth/callback` (for local development)
7. Note down your:
   - Client ID
   - Client Secret

## Step 4: Configure Environment Variables

### Frontend (.env)
```env
VITE_SUPABASE_URL=https://your-project-id.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

### Backend (.env)
```env
DATABASE_URL=sqlite:///./homework_app.db

# Supabase
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# JWT - Generate a secure random key for production
JWT_SECRET_KEY=your-secure-jwt-secret-key

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/callback
```

#### Important: JWT_SECRET_KEY Configuration

The `JWT_SECRET_KEY` is used to sign and verify JWT tokens that the backend generates for API authentication. This is **different** from Supabase tokens.

**For development:**
- Use any random string, e.g., `development-secret-key-12345`

**For production:**
- **NEVER** use the default value `your-secret-key-here-change-in-production`
- Generate a secure random key using one of these methods:

```bash
# Method 1: Using openssl
openssl rand -hex 32

# Method 2: Using Python
python -c "import secrets; print(secrets.token_hex(32))"

# Method 3: Using Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

Example secure key: `f8d2a3b1c4e5f6789a0b1c2d3e4f5678901234567890abcdef1234567890abcd`

## Step 5: Configure Google OAuth in Supabase

1. Return to Supabase Authentication > Providers > Google
2. Enter your Google Client ID and Client Secret
3. Save the configuration

## Step 6: Update Google OAuth Scopes

The app requests the following Google OAuth scopes:
- `openid` - Basic user information
- `email` - User's email address
- `profile` - User's profile information
- `https://www.googleapis.com/auth/calendar` - Google Calendar access

## How the Authentication Flow Works

1. **User clicks "Sign in with Google"** - Triggers Supabase OAuth flow
2. **Redirect to Google** - User authorizes the app with Google
3. **Google redirects back** - With authorization code to Supabase
4. **Supabase handles tokens** - Exchanges code for tokens and creates session
5. **Frontend receives session** - With user data and Google tokens from Supabase
6. **Backend user creation** - Frontend calls `/api/auth/google/callback` with Google tokens
7. **Backend JWT token** - Backend creates/updates user and returns its own JWT token
8. **Frontend token switch** - Frontend switches from Supabase JWT to backend JWT for API calls
9. **Calendar sync** - Automatically syncs existing homework with Google Calendar

### Token Flow Explained

The app uses **two different JWT tokens**:

1. **Supabase JWT Token**: 
   - Created by Supabase after Google OAuth
   - Used only for the initial backend authentication call
   - Contains Supabase user information

2. **Backend JWT Token**:
   - Created by your backend server using `JWT_SECRET_KEY`
   - Used for all subsequent API calls to your backend
   - Contains your app's user ID and permissions

This dual-token approach allows you to:
- Leverage Supabase's OAuth handling
- Maintain your own user database and permissions
- Keep full control over API authentication

## Features Implemented

### Frontend
- ✅ Supabase client configuration
- ✅ Google OAuth sign-in button
- ✅ AuthContext with Supabase integration
- ✅ OAuth callback handling
- ✅ Automatic session management
- ✅ Loading states and error handling

### Backend
- ✅ User model with Google token storage
- ✅ Google OAuth callback endpoint
- ✅ JWT token generation for app authentication
- ✅ Google Calendar service integration
- ✅ Calendar sync endpoints
- ✅ Automatic homework-to-calendar sync

### Security Features
- ✅ Secure token storage in Supabase
- ✅ JWT tokens for backend API access
- ✅ Google token refresh handling
- ✅ CORS configuration for secure requests

## Testing the Setup

1. Start the backend server: `cd backend && python run.py`
2. Start the frontend server: `cd frontend && npm run dev`
3. Navigate to `http://localhost:3000`
4. Click "Sign in with Google"
5. Complete Google OAuth flow
6. Should redirect to dashboard with user profile
7. Create a homework assignment
8. Check Google Calendar for automatic sync

## Troubleshooting

### Common Issues

1. **"your-project.supabase.co is blocked"**
   - Update your `.env` files with real Supabase URLs

2. **OAuth redirect mismatch**
   - Ensure redirect URIs match in Google Console and Supabase

3. **Calendar sync fails**
   - Check Google Calendar API is enabled
   - Verify Google OAuth scopes include calendar access

4. **Backend authentication errors ("API denies everything")**
   - **Most common cause**: Using default `JWT_SECRET_KEY`
   - **Solution**: Generate a proper JWT secret key (see JWT_SECRET_KEY section above)
   - Check Supabase service role key is correct
   - Verify the backend is receiving and using the correct JWT token

5. **"Could not validate credentials" errors**
   - Ensure you're using the backend JWT token (not Supabase JWT) for API calls
   - Check that JWT_SECRET_KEY matches between token creation and verification
   - Verify token hasn't expired (default: 7 days)

### Debug Mode

Set these environment variables for debugging:
```env
# Frontend
VITE_DEBUG=true

# Backend
LOG_LEVEL=DEBUG
```

## API Endpoints

### Authentication
- `POST /api/auth/google/callback` - Handle Google OAuth callback
- `GET /api/auth/me` - Get current user profile

### Calendar Sync
- `POST /api/calendar/sync` - Sync all homework with calendar
- `POST /api/calendar/sync/{homework_id}` - Sync specific homework

## Next Steps

After setting up authentication, you can:
1. Create homework assignments that automatically sync to Google Calendar
2. View and manage your schedule
3. Get reminders and notifications
4. Access your data securely across devices