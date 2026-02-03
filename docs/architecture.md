# Project Architecture

## Overview

The 1x-fit bot is a Telegram bot for fitness tracking and weight loss competition. It uses a modular architecture with clear separation of concerns.

## Directory Structure

```
bot/
├── main.py                 # Entry point and main application setup
├── settings.py             # Application settings and configuration
├── requirements.txt        # Python dependencies
├── Dockerfile             # Container configuration
├── database/              # Database models and initialization
│   └── models.py
├── handlers/              # Telegram bot command handlers
│   ├── __init__.py
│   ├── daily_polls.py     # Weight and activity input handlers
│   ├── notifications.py   # Notification scheduling and sending
│   ├── progress.py        # Progress tracking and visualization commands
│   └── registration.py    # User registration flow
└── utils/                 # Utility functions
    ├── calculations.py    # Progress calculation algorithms
    └── visualization.py   # Chart generation functions
```

## Core Components

### 1. Main Application (main.py)

- Initializes the bot with proper settings
- Sets up the dispatcher and registers handlers
- Configures webhook or polling mode
- Starts the notification scheduler
- Handles application lifecycle events

### 2. Settings (settings.py)

- Centralized configuration using Pydantic Settings
- Environment variable loading
- Configuration for bot token, database path, notification times, etc.

### 3. Database Layer (database/models.py)

- SQLite database schema definition
- Table creation and initialization
- Default activity types setup
- Index definitions for performance

### 4. Handlers

#### Registration Handler
- Manages user registration flow using FSM
- Collects user profile information (name, gender, age, height, weights)

#### Daily Polls Handler
- Handles weight input commands
- Processes activity input with keyboard selections
- Manages activity type selection FSM

#### Progress Handler
- Displays user progress information
- Generates individual and comparison charts
- Shows activity statistics

#### Notifications Handler
- Manages scheduled notifications using APScheduler
- Sends daily reminders for weight and activity input

### 5. Utilities

#### Calculations
- BMI calculation algorithms
- Progress scoring formulas
- Calorie calculation functions

#### Visualization
- Chart generation for individual progress
- Comparison charts for all participants
- Activity visualization

## Deployment Architecture

The bot is deployed as a Docker container with:

- Persistent volumes for database and chart storage
- Environment-based configuration
- Webhook-based communication with Telegram
- Scheduled notifications using APScheduler

## External Dependencies

- aiogram: Telegram Bot API framework
- APScheduler: Advanced Python Scheduler for notifications
- SQLite: Local database storage
- Matplotlib/Seaborn: Chart generation
- Pydantic: Settings and data validation