# Messaging Service (Django Channels) — Ready to Run

Features:
- Django REST endpoints for creating/getting rooms + listing messages
- WebSocket (Daphne/Channels) one-to-one chat
- JWT validation (local decode) for auth (supports HS256/RS256)
- Optional profile fetching from external Auth API
- Presence and typing indicators via WebSocket
- Redis channel layer & PostgreSQL persistence
- Docker + docker-compose example

## Quickstart 

1. Copy `.env.example` to `.env` and fill values (point `AUTH_API_URL` and `JWT_SECRET` to your Auth service).
2. Build & start:
   ```bash
   docker-compose up --build
