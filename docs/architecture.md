# System Architecture

The ApnaSamaj platform follows a scalable, decoupled Microservices-inspired Monorepo approach.

## Multi-Tenant Backend (FastAPI)

Located in `apps/api/`, the backend is built with FastAPI. It handles core business logic and database interactions securely.

- **Multi-Tenancy**: Every database request requires an `X-Tenant-ID` header. The repository layer strictly injects `tenant_id == self.tenant_id` into every SQL statement to prevent cross-community data bleeding.
- **Async Processing**: Powered by SQLAlchemy 2.0 Asyncio and `asyncpg` for maximum throughput during heavy events like broadcasting notifications to thousands of members.

## Web Admin Dashboard (Next.js)

Located in `apps/web/`, this React application relies heavily on modern Web Design principles.

- **Vanilla CSS Ecosystem**: No Tailwind. We rely on a global design system of variables targeting CSS properties like `backdrop-filter` for glassmorphism.
- **Client-Side Data Grids**: Provides high-level Metric displays and extensive Datagrids for managing Members, Donations, and Polls.

## Mobile Application (Expo / React Native)

Located in `apps/mobile/`, this is the member-facing client.

- **5-Tab Navigation**: Built using Expo Router (`_layout.tsx`) bridging Home, Directory, Events, Donations, and Profile.
- **Deep Integrations**: Communicates with the backend using Axios request interceptors that attach the JWT Auth Token.
