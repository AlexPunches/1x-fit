# 1x-fit

Telegram bot for fitness tracking and weight loss competition with fair progress tracking.

## Features

- Weight tracking with progress visualization
- Activity tracking (walking, running, cycling, cardio)
- Personalized progress charts
- Daily reminders and notifications
- Comparison with other participants

## CI/CD Pipeline

The project uses GitHub Actions for continuous integration and deployment:

- **Build & Push**: Automatically builds Docker images on every commit to `main`/`develop` branches and pull requests
- **Deploy**: Manual deployment triggered via GitHub Actions UI

For more details, see [CI/CD Workflow Documentation](./docs/cicd_workflow.md).

## Setup

1. Copy `.env.example` to `.env` and fill in your bot token
2. Install dependencies: `uv pip install -r bot/requirements.txt`
3. Run the bot: `cd bot && python main.py`

## Commands

See [BOT_COMMANDS.md](./BOT_COMMANDS.md) for a list of available bot commands.
