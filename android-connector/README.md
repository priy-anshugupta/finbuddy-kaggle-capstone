# FinBuddy Connector - Android App

A companion Android app for FinBuddy that automatically extracts and syncs financial transactions from SMS messages to your FinBuddy dashboard.

## Features

- 🔐 **Secure Login**: Connect with your existing FinBuddy account
- 📱 **SMS Extraction**: Automatically reads financial SMS from banks and payment apps
- 🤖 **Smart Parsing**: Extracts transaction details (amount, merchant, type, etc.)
- 🔄 **Auto Sync**: Periodically syncs new transactions to your dashboard
- 🔔 **Real-time Sync**: Immediately syncs new SMS when received
- 🔒 **Privacy First**: SMS data is processed locally, only parsed data is sent

## Supported Banks & Services

The app supports SMS parsing from major banks and payment services:

### Banks (India)
- HDFC Bank
- ICICI Bank
- State Bank of India (SBI)
- Axis Bank
- Kotak Mahindra Bank
- IDFC First Bank
- Yes Bank
- Punjab National Bank
- Bank of Baroda
- IndusInd Bank
- And more...

### Payment Services
- Paytm
- Google Pay
- PhonePe
- Amazon Pay
- Mobikwik
- Freecharge

## Requirements

- Android 8.0 (API 26) or higher
- SMS permission for reading bank messages
- Internet connection for syncing

## Installation

### From Source

1. Open the project in Android Studio
2. Sync Gradle files
3. Update `API_BASE_URL` in `app/build.gradle.kts` to your backend URL
4. Build and run on your device

### Configuration

Update the backend URL in `app/build.gradle.kts`:

```kotlin
buildConfigField("String", "API_BASE_URL", "\"https://your-server.com/api/v1/\"")
```

## Architecture

```
app/
├── data/
│   ├── local/          # DataStore preferences
│   ├── remote/         # Retrofit API service
│   ├── model/          # Data models
│   └── repository/     # Data repositories
├── di/                 # Hilt dependency injection
├── sms/                # SMS parsing and receiving
├── sync/               # Background sync workers
├── ui/                 # Activities and ViewModels
└── utils/              # Utility classes
```

## Tech Stack

- **Language**: Kotlin
- **DI**: Hilt
- **Networking**: Retrofit + OkHttp
- **Background Work**: WorkManager
- **Preferences**: DataStore
- **Architecture**: MVVM

## Permissions

The app requires the following permissions:

| Permission | Purpose |
|------------|---------|
| `READ_SMS` | Read bank SMS messages |
| `RECEIVE_SMS` | Receive new SMS in real-time |
| `INTERNET` | Sync data with backend |
| `POST_NOTIFICATIONS` | Show sync notifications |

## API Endpoints

The app communicates with the following backend endpoints:

- `POST /api/v1/auth/login` - User authentication
- `POST /api/v1/sms/transactions` - Upload single transaction
- `POST /api/v1/sms/transactions/batch` - Upload multiple transactions
- `GET /api/v1/sms/sync-status` - Get sync status

## Privacy & Security

- SMS messages are parsed **locally on your device**
- Only structured transaction data is sent to the server
- Tokens are stored securely using encrypted preferences
- No SMS content is stored on the server (only parsed data)

## Development

### Building

```bash
# Debug build
./gradlew assembleDebug

# Release build
./gradlew assembleRelease
```

### Testing

```bash
./gradlew test
./gradlew connectedAndroidTest
```

## License

This project is part of the FinBuddy Financial Assistant application.
