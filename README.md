# LLM FastAPI + React + Supabase Starter

## Quick Start

1. **Create a [Supabase](https://supabase.com/) project.**  
   Get your project URL and anon key, add to both backend/.env and frontend/.env.

2. **Clone this repo** and fill in all `.env` files as needed.

3. **Start everything with Docker Compose:**  
   ```bash
   docker-compose up --build
   ```
   - Backend: [http://localhost:8000](http://localhost:8000)
   - Frontend: [http://localhost:5173](http://localhost:5173)

4. **Sign up/login on the frontend and try the LLM chat!**

## Features

- Async FastAPI backend with JWT auth, per-user rate limiting (Redis), and LLM endpoint.
- React Vite frontend with login/signup and chat to LLM.
- Supabase/Postgres for user management.
- Ready to extend for your own LLM calls.

## Customizing

- Replace the dummy LLM call in `backend/main.py` with your preferred LLM API.
- Adjust rate limits as needed.

---

**Happy hacking!**
