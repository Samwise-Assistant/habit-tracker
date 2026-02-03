# 🎯 Habit Tracker

A simple, beautiful habit tracking web app with GitHub OAuth login.

## Features

- ✅ **Track daily habits** with custom icons and colors
- 🔥 **Streak tracking** - build and maintain your streaks
- 📊 **Heatmap view** - visualize your progress over time
- 📱 **Mobile friendly** - works on all devices
- 🔐 **GitHub OAuth** - simple, secure login

## Tech Stack

- **Flask** - Python web framework
- **SQLite** - Simple database
- **Tailwind CSS** - Modern styling
- **GitHub OAuth** - Authentication

## Setup

```bash
# Clone and enter directory
cd habit-tracker

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt
npm install

# Configure GitHub OAuth
# 1. Go to https://github.com/settings/developers
# 2. Create a new OAuth App:
#    - Homepage URL: http://localhost:5000
#    - Callback URL: http://localhost:5000/login/github/callback
# 3. Copy .env.example to .env and fill in your credentials

# Run the app
npm run dev   # Build CSS (in one terminal)
flask --app app run --debug  # Run Flask (in another terminal)
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Flask secret key (change in production!) |
| `GITHUB_CLIENT_ID` | GitHub OAuth Client ID |
| `GITHUB_CLIENT_SECRET` | GitHub OAuth Client Secret |

## Project Structure

```
habit-tracker/
├── app/
│   ├── __init__.py      # App setup and models
│   ├── routes.py        # All routes
│   └── templates/       # HTML templates
│       ├── base.html
│       ├── index.html
│       └── dashboard.html
├── static/
│   └── css/            # Tailwind CSS output
├── requirements.txt
├── package.json
└── tailwind.config.js
```

## License

MIT
