# iOS Shortcut: Log Activity

This shortcut allows you to quickly log activities from your iPhone using voice dictation.

## Setup Instructions

### 1. Install Pushover App

1. Download **Pushover** from the App Store ($4.99 one-time purchase)
2. Create an account at [pushover.net](https://pushover.net)
3. Note your **User Key** (shown on the main dashboard)
4. Create a new application at [pushover.net/apps/build](https://pushover.net/apps/build):
   - Name: "Time Tracker"
   - Type: Script/Application
   - Note the **API Token**

### 2. Create the Shortcut

Open the **Shortcuts** app on your iPhone and create a new shortcut with these actions:

#### Step 1: Get Input
- Add action: **Shortcut Input**
- This captures any input passed from Pushover notification

#### Step 2: Set Ping ID Variable
- Add action: **Set Variable**
- Variable name: `ping_id`
- Value: Shortcut Input (or empty if manual)

#### Step 3: Dictate Activity
- Add action: **Dictate Text**
- Settings:
  - Language: English
  - Stop Listening: After Short Pause

#### Step 4: Set Activity Variable
- Add action: **Set Variable**
- Variable name: `activity_text`
- Value: Dictated Text

#### Step 5: Determine Entry Type
- Add action: **If**
- Condition: `ping_id` has any value
  - **Then**: Set Variable `entry_type` to "ping_response"
  - **Otherwise**: Set Variable `entry_type` to "manual"

#### Step 6: Send to Supabase
- Add action: **Get Contents of URL**
- URL: `https://ydwjzlikslebokuxzwco.supabase.co/rest/v1/activity_logs`
- Method: POST
- Headers:
  - `apikey`: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inlkd2p6bGlrc2xlYm9rdXh6d2NvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg4NTEwODAsImV4cCI6MjA4NDQyNzA4MH0.CUPTmjww31xOS0-qknpQHByC3ACZ4lk1CiBcVZXHThU`
  - `Authorization`: `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inlkd2p6bGlrc2xlYm9rdXh6d2NvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg4NTEwODAsImV4cCI6MjA4NDQyNzA4MH0.CUPTmjww31xOS0-qknpQHByC3ACZ4lk1CiBcVZXHThU`
  - `Content-Type`: `application/json`
  - `Prefer`: `return=representation`
- Request Body (JSON):
```json
{
  "activity_text": "[activity_text variable]",
  "input_method": "voice",
  "device": "iphone",
  "entry_type": "[entry_type variable]"
}
```

#### Step 7: Parse Response
- Add action: **Get Dictionary Value**
- Key: `activity_text`
- Dictionary: Contents of URL result

#### Step 8: Speak Confirmation
- Add action: **Speak Text**
- Text: "Logged: [activity_text]"

### 3. Configure Shortcut Settings

1. Tap the shortcut name → Settings (gear icon)
2. Enable "Show in Share Sheet"
3. Add to Home Screen for quick access
4. Set up Siri phrase: "Hey Siri, log activity"

### 4. Configure Pushover to Use Shortcut

When the Mac app sends a ping, it includes a URL that opens this shortcut:

```
shortcuts://run-shortcut?name=Log%20Activity&input=text&text=PING_ID
```

To test manually, tap the Pushover notification and it should open the shortcut.

## Alternative: Simple Version

If the above is too complex, here's a simpler 3-step shortcut:

1. **Dictate Text** - Ask "What are you doing?"
2. **Get Contents of URL** - POST to Supabase with dictated text
3. **Speak Text** - Say "Logged: [dictated text]"

This version won't track ping responses but works for manual logging.

## Trigger Options

- **Tap Pushover notification** - Opens shortcut with ping ID
- **Home screen icon** - Manual logging
- **"Hey Siri, log activity"** - Voice trigger
- **Back Tap** (Settings → Accessibility → Touch → Back Tap) - Physical trigger

## Troubleshooting

### "Unable to connect"
- Check your internet connection
- Verify the API key is correct (copy exactly as shown)

### Voice dictation not working
- Enable Dictation in Settings → General → Keyboard
- Ensure microphone access is granted to Shortcuts

### Notification doesn't open shortcut
- Make sure shortcut name matches exactly: "Log Activity"
- Test the URL manually in Safari first

## Quick Test

Run the shortcut manually and say "Testing time tracker".
Then open the web dashboard to verify the entry appears.
