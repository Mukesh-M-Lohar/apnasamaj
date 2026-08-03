# Project Rules

## Playwright & Next.js Port Collisions
Before running Web E2E tests (`npx playwright test`) or starting the Next.js dev server, ALWAYS verify that port 3000 is available. If a zombie `next dev` process is occupying port 3000, kill it first (e.g., using `fuser -k 3000/tcp` or `kill <PID>`). This ensures the dev server binds to port 3000, which is the URL that Playwright targets by default, preventing false test failures and timeouts.
