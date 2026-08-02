# ApnaSamaj – Architecture Overview

## System Architecture

ApnaSamaj uses a **Modular Monolith** architecture – all business modules live in a single deployable unit but maintain strict boundaries.

```
┌─────────────────────────────────────────────────────────────┐
│                     API Gateway (FastAPI)                     │
│   CORS │ Rate Limit │ Auth │ Tenant Context │ Secure Headers │
├─────────────────────────────────────────────────────────────┤
│                        API v1 Routes                         │
├──────┬──────┬──────┬──────┬──────┬──────┬──────┬────────────┤
│ Auth │Comm- │Memb- │Fami- │Comm- │Dona- │Event │ Volunteer  │
│      │unity │er    │ly    │ittee │tion  │      │            │
├──────┴──────┴──────┴──────┴──────┴──────┴──────┴────────────┤
│                      Service Layer                           │
│              Business Logic │ Validation │ Auth               │
├─────────────────────────────────────────────────────────────┤
│                     Repository Layer                         │
│            SQLAlchemy 2.0 │ Async │ Tenant-scoped            │
├─────────────────────────────────────────────────────────────┤
│                      Data Layer                              │
│  PostgreSQL │ Redis │ MinIO │ Celery                         │
└─────────────────────────────────────────────────────────────┘
```

## Multi-Tenant Strategy

**Row-level isolation** using `tenant_id` FK on every business table.

- Every query is automatically scoped to the current tenant
- The `BaseRepository` enforces tenant filtering on all operations
- Super Admin can access data across tenants via header override

## Module Structure

Each business module follows this structure:

```
modules/<module_name>/
├── __init__.py
├── models.py          # SQLAlchemy models
├── schemas.py         # Pydantic request/response schemas
├── repository.py      # Database operations
├── service.py         # Business logic
├── routes.py          # FastAPI API endpoints
├── permissions.py     # Module-specific permissions
└── tests/
    ├── test_routes.py
    ├── test_service.py
    └── test_repository.py
```

## Design Patterns

| Pattern | Where | Why |
|---------|-------|-----|
| Repository | `base_repository.py` + per-module | Decouple DB from business logic |
| Service Layer | Per-module `service.py` | Encapsulate business rules |
| Dependency Injection | FastAPI `Depends()` | Testability, loose coupling |
| Factory | `create_app()` in `main.py` | Configurable app creation |
| Strategy | Permissions system | Configurable role→permission mapping |
| Observer | Audit logs | Track changes without coupling |

## Security Architecture

```
Mobile App / Web ──→ HTTPS ──→ FastAPI
                                  │
                          ┌───────┴────────┐
                          │ Rate Limiting   │
                          │ Secure Headers  │
                          │ CORS            │
                          │ Input Validation │
                          └───────┬────────┘
                                  │
                          ┌───────┴────────┐
                          │ JWT Auth        │
                          │ + RBAC Check    │
                          │ + Tenant Scope  │
                          └───────┬────────┘
                                  │
                          ┌───────┴────────┐
                          │ Business Logic  │
                          │ Audit Logging   │
                          └───────┬────────┘
                                  │
                          ┌───────┴────────┐
                          │ PostgreSQL      │
                          │ (parameterized  │
                          │  queries only)  │
                          └────────────────┘
```

## Technology Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Runtime | Python | 3.13 |
| Framework | FastAPI | 0.115+ |
| ORM | SQLAlchemy | 2.0+ |
| Migrations | Alembic | 1.14+ |
| Validation | Pydantic | 2.10+ |
| Database | PostgreSQL | 16 |
| Cache | Redis | 7 |
| Queue | Celery | 5.4 |
| Storage | MinIO | Latest |
| Frontend | React + TypeScript + Vite | Latest |
| Mobile | React Native + Expo | Latest |
| Container | Docker + Compose | Latest |
