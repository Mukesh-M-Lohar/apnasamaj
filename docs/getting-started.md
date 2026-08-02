# Getting Started

Follow these steps to run the entire ApnaSamaj ecosystem locally using Docker.

## Prerequisites
- [Docker & Docker Compose](https://www.docker.com/)
- [Python 3.12](https://www.python.org/)
- [Node.js 20+](https://nodejs.org/)

## 1. Local Environment Orchestration

You can spin up the entire ecosystem in one command. At the root of your project:

```bash
make run-docker
```

This starts:
- PostgreSQL (Database)
- Redis (Queue/Cache)
- MinIO (Storage)
- FastAPI (Backend APIs)
- Next.js (Web Admin Dashboard)
- Expo (React Native Bundler)

> **Screenshot Placeholder:**
> *(Drop an image of your terminal running docker-compose here!)*
> `![Docker Terminal](assets/docker-terminal.png)`

---

## 2. Seeding the Database

To test the applications, you'll need data. In a separate terminal, run:

```bash
make seed
```
*This command invokes `scripts/seed.py`, safely connecting to your local PostgreSQL instance and injecting dummy members, a mock admin (`Admin@123`), events, and facility ledgers.*

---

## 3. Launching the Web Admin Dashboard

With the backend and database running, the Next.js app is available at:
`http://localhost:3000`

> **Screenshot Placeholder:**
> *(Drop an image of your Web Dashboard here!)*
> `![Web Dashboard](assets/web-dashboard.png)`

---

## 4. Launching the Mobile App

Since you used `make run-docker`, the Metro bundler is running in a container.
In the logs, look for the Expo QR code.

1. Download **Expo Go** on your iOS/Android phone.
2. Ensure your phone is on the **same Wi-Fi network** as your computer.
3. Scan the QR code.

> **Screenshot Placeholder:**
> *(Drop an image of the Mobile App home screen here!)*
> `![Mobile App](assets/mobile-app.png)`
