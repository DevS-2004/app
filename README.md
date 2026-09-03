<div align="center">

# 🕳️ Wumpus Cave: Echoes of the Deep

> *Navigate the darkness. Trust your senses. Hunt or be hunted.*

[![Language](https://img.shields.io/badge/Language-JavaScript%20%7C%20Python-blue?style=flat-square)](https://github.com/DevS-2004/app)
[![Frontend](https://img.shields.io/badge/Frontend-React-61DAFB?style=flat-square&logo=react)](https://reactjs.org/)
[![Backend](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Database](https://img.shields.io/badge/Database-MongoDB-47A248?style=flat-square&logo=mongodb)](https://www.mongodb.com/)
[![Styling](https://img.shields.io/badge/Styling-Tailwind%20CSS-38B2AC?style=flat-square&logo=tailwindcss)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

A modern, full-stack reimagining of the classic **Hunt the Wumpus** game — built with a dark fantasy aesthetic, real-time sensory feedback, and a persistent leaderboard.

</div>

---

## 📖 Table of Contents

- [About the Game](#-about-the-game)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [Environment Variables](#-environment-variables)
- [API Reference](#-api-reference)
- [Gameplay Guide](#-gameplay-guide)
- [Design System](#-design-system)
- [Testing](#-testing)
- [Contributing](#-contributing)

---

## 🎮 About the Game

**Wumpus Cave: Echoes of the Deep** is a browser-based survival game set on an **8×8 fog-of-war grid**. You are an explorer who has descended into a monster-infested cave. Your mission: **find the gold and escape alive** — without falling into a pit, getting carried away by giant bats, or being devoured by the Wumpus.

The game is driven by *sensory clues*: you cannot see the entire cave, but you can *hear* and *smell* what lurks in adjacent cells.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🗺️ **8×8 Fog-of-War Grid** | Only visited cells are revealed; the rest remains shrouded in darkness |
| 👹 **The Wumpus** | A single deadly monster lurking in the cave — shoot it to clear a path |
| 🕳️ **Pit Traps** | Three bottomless pits scattered across the cave — fall in and it's over |
| 🦇 **Giant Bats** | Two bats that teleport you to a random cell when encountered |
| 🏆 **Gold** | Collect the treasure and make it back to the entrance to win |
| 🏹 **Arrows** | You start with 3 arrows — use them wisely to shoot the Wumpus |
| 📡 **Sensory Feedback** | Perceive *breezes* (pits), *stenches* (Wumpus), *flutters* (bats), and *glimmers* (gold) |
| 📊 **Leaderboard** | Persistent MongoDB-backed leaderboard to track top scores |
| 🌑 **Dark Fantasy UI** | Atmospheric dark theme with glowing entity indicators |

---

## 🛠️ Tech Stack

### Frontend
- **[React](https://reactjs.org/)** — Component-based UI framework
- **[Tailwind CSS](https://tailwindcss.com/)** — Utility-first styling
- **[Radix UI](https://www.radix-ui.com/)** — Accessible, unstyled UI primitives
- **[CRACO](https://craco.js.org/)** — Create React App Configuration Override
- **Fonts:** Cinzel (headings), Inter (body), JetBrains Mono (stats)

### Backend
- **[FastAPI](https://fastapi.tiangolo.com/)** — High-performance async Python web framework
- **[Motor](https://motor.readthedocs.io/)** — Async MongoDB driver
- **[Pydantic v2](https://docs.pydantic.dev/)** — Data validation and serialization
- **[Uvicorn](https://www.uvicorn.org/)** — ASGI server

### Database
- **[MongoDB](https://www.mongodb.com/)** — NoSQL database for game state and leaderboard persistence

---

## 📁 Project Structure

```
app/
├── backend/
│   ├── server.py          # FastAPI app — game logic, routes, DB models
│   ├── requirements.txt   # Python dependencies
│   └── .env               # Backend environment variables (not committed)
│
├── frontend/
│   ├── src/
│   │   ├── App.js         # Root React component — main game UI & state
│   │   ├── App.css        # Component-level styles
│   │   ├── index.js       # React entry point
│   │   ├── index.css      # Global styles & Tailwind directives
│   │   ├── components/    # Reusable UI components
│   │   ├── hooks/         # Custom React hooks
│   │   └── lib/           # Utility functions
│   ├── public/            # Static assets
│   ├── plugins/           # CRACO/webpack plugins
│   ├── package.json       # Node.js dependencies
│   ├── tailwind.config.js # Tailwind CSS configuration
│   ├── craco.config.js    # CRA configuration override
│   └── .env               # Frontend environment variables (not committed)
│
├── tests/                 # Test suites
├── test_reports/          # Generated test reports
├── memory/                # Agent memory/state persistence
├── backend_test.py        # Backend integration tests
├── test_result.md         # Test run results log
├── design_guidelines.json # Full design system specification
├── yarn.lock              # Root yarn lockfile
└── .gitignore
```

---

## 🚀 Getting Started

### Prerequisites

Make sure you have the following installed:

- **Node.js** ≥ 18.x and **Yarn**
- **Python** ≥ 3.10
- A running **MongoDB** instance (local or [MongoDB Atlas](https://www.mongodb.com/atlas))

---

### Backend Setup

```bash
# 1. Navigate to the backend directory
cd backend

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate       # Linux/macOS
# OR
venv\Scripts\activate          # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env           # then fill in your values (see below)

# 5. Start the development server
uvicorn server:app --reload --port 8001
```

The API will be available at `http://localhost:8001`.  
Interactive docs: `http://localhost:8001/docs`

---

### Frontend Setup

```bash
# 1. Navigate to the frontend directory
cd frontend

# 2. Install dependencies
yarn install

# 3. Configure environment variables
cp .env.example .env           # then fill in your values (see below)

# 4. Start the development server
yarn start
```

The app will be available at `http://localhost:3000`.

---

## 🔑 Environment Variables

### `backend/.env`

```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=wumpus_cave
```

### `frontend/.env`

```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

---

## 📡 API Reference

All endpoints are prefixed with `/api`.

### Game Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/games` | Start a new game — returns initial `GameState` |
| `GET` | `/api/games/{game_id}` | Get current state of a game |
| `POST` | `/api/games/move` | Move the player in a direction |
| `POST` | `/api/games/shoot` | Shoot an arrow in a direction |

### Leaderboard Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/leaderboard` | Retrieve the top scores |
| `POST` | `/api/leaderboard` | Submit a score after winning |

### Request / Response Examples

**Move Request**
```json
{
  "game_id": "uuid-string",
  "direction": "up"   // "up" | "down" | "left" | "right"
}
```

**Game State Response**
```json
{
  "game_id": "uuid-string",
  "player_position": { "x": 0, "y": 1 },
  "arrows_remaining": 3,
  "moves_count": 1,
  "has_gold": false,
  "game_status": "active",
  "score": 0,
  "visited_cells": [[true, true], [false, false], ...],
  "sensory_info": {
    "breeze": false,
    "stench": true,
    "flutter": false,
    "glimmer": false
  },
  "message": "You sense a foul stench nearby..."
}
```

---

## 🎯 Gameplay Guide

### Objective
Find the **gold** 🏆, then navigate back to the **starting cell (0, 0)** to win.

### Controls
Use the **arrow keys** or **on-screen direction buttons** to move.  
Use the **shoot button** + a direction to fire an arrow.

### Sensory Clues

| Clue | Meaning |
|---|---|
| 💨 **Breeze** | A pit is in an adjacent cell |
| 🤢 **Stench** | The Wumpus is in an adjacent cell |
| 🦇 **Flutter** | Bats are in an adjacent cell |
| ✨ **Glimmer** | Gold is in this or an adjacent cell |

### Scoring

| Action | Points |
|---|---|
| Winning (collecting gold + escaping) | **+1000** |
| Each move | **−1** |
| Firing an arrow | **−10** |
| Killing the Wumpus | **+500** |
| Falling into a pit | **Game Over** |
| Being eaten by the Wumpus | **Game Over** |

### Game Entities

| Symbol | Entity | Effect |
|---|---|---|
| 👹 | **Wumpus** | Instant death on contact |
| 🕳️ | **Pit** | Instant death on contact |
| 🦇 | **Bats** | Teleport you to a random cell |
| 🏆 | **Gold** | Pick it up — then get out! |

---

## 🎨 Design System

The visual identity is defined in [`design_guidelines.json`](design_guidelines.json) and follows the **"Dark Fantasy meets Retro-Terminal"** aesthetic.

### Color Palette

| Token | Hex | Usage |
|---|---|---|
| Background | `#0a0a0a` | Page background |
| Card | `#121212` | Game board, panels |
| Border | `#2a2a2a` | Cell borders |
| Primary | `#e11d48` | Danger, Wumpus |
| Secondary | `#2563eb` | Pits, information |
| Accent | `#f59e0b` | Gold, highlights |
| Muted | `#525252` | Subdued text |

### Typography

| Role | Font |
|---|---|
| Headings | Cinzel, serif |
| Body | Inter, sans-serif |
| Stats / HUD | JetBrains Mono, monospace |

---

## 🧪 Testing

### Backend Tests

```bash
# From the project root
python -m pytest backend_test.py -v

# Or from the tests/ directory
python -m pytest tests/ -v
```

### Frontend Tests

```bash
cd frontend
yarn test
```

Test reports are saved to the `test_reports/` directory.

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. **Fork** this repository
2. **Create** a feature branch: `git checkout -b feature/your-feature`
3. **Commit** your changes: `git commit -m "feat: add your feature"`
4. **Push** to your branch: `git push origin feature/your-feature`
5. **Open** a Pull Request

### Code Style

- **Python**: `black` + `isort` + `flake8` (configs in `requirements.txt`)
- **JavaScript**: Follow the existing ESLint/Prettier config in the project

---

## 👤 Author

**DevS-2004** — [@DevS-2004](https://github.com/DevS-2004)

---

<div align="center">

*Will you conquer the cave... or become part of it?* 🕳️

</div>
