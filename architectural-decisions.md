# Architectural Decisions

This document summarises the architectural patterns used by the backend in `app/`. It is a living description of how the code is organised, not a full ADR log.

## Goals

- Keep HTTP, persistence, and LLM infrastructure out of application use cases.
- Make write and read flows explicit and separately evolvable.
- Allow infrastructure to be replaced behind interfaces without rewriting handlers.
- Keep transactions coherent across multiple repository operations.

## High-level shape (onion / ports-and-adapters style)

Dependencies point inward toward application behaviour.

| Layer | Location | Responsibility |
| --- | --- | --- |
| Presentation | `controllers/`, `auth/current_user_dependency.py`, `main.py` | HTTP routes, cookies, status codes, wiring |
| Application | `command_handlers/`, `query_handlers/`, `auth/*_service.py`, `commands/`, `queries/`, `exceptions/` | Use cases, auth rules, domain-facing exceptions |
| Ports | `abstractions/` | Interfaces owned by the application |
| Adapters / infrastructure | `db/`, `kernel/`, `utils/mediator.py` (composition helper) | SQLAlchemy, Semantic Kernel/Ollama, concrete UoW |
| Shared contracts | `data_transfer_objects/`, `models/` | Immutable request/response and application types |

`main.py` is the composition root: it constructs concrete adapters and injects them into controllers and handlers.

## Dependency Inversion Principle (DIP)

Application code depends on abstractions, not on FastAPI, SQLAlchemy sessions, or Semantic Kernel types.

Examples:

- `IUnitOfWorkFactory` / `IUnitOfWork` / repository interfaces in `abstractions/`
- `IChatCompletion` for LLM completion; implemented by `SemanticKernelChatCompletion`
- Handlers take `IUnitOfWorkFactory` and `IChatCompletion` via constructors
- Controllers take a `Mediator` and auth adapters; they do not open database sessions themselves

Concrete classes live in `db/` and `kernel/` and implement those ports.

## CQRS and Mediator

Command/Query Responsibility Segregation is applied at the application boundary.

- **Commands** (`commands/`) represent writes, for example `ChatCommand`.
- **Queries** (`queries/`) represent reads, for example `ConversationMessagesQuery` and `ConversationSummariesQuery`.
- **Command handlers** (`command_handlers/`) and **query handlers** (`query_handlers/`) contain the use-case logic.
- A handmade **`Mediator`** (`utils/mediator.py`) accepts `ICommand | IQuery` and dispatches with a `match` on the message type.

Controllers send messages through the mediator instead of calling handlers directly. That keeps the HTTP layer thin and makes the set of application entry points visible in one place.

## Unit of Work and Repository

Persistence is accessed through repositories grouped by a unit of work.

- `IUnitOfWork` exposes `conversationRepository`, `userRepository`, and `sessionRepository`.
- `UnitOfWork` opens one async SQLAlchemy session, commits on success, rolls back on failure, and closes the session in `__aexit__`.
- `UnitOfWorkFactory` creates a new unit of work per use-case scope (`async with factory.create()`).
- Repositories implement the port interfaces and map between database records and application/DTO types.

This keeps multi-step writes (for example create user + create session) in a single transaction.

## Controllers as HTTP adapters

`ConversationsController` and `SessionsController` own FastAPI `APIRouter`s under `/api/conversations` and `/api/sessions`.

- Construction-time dependencies (mediator, services, settings) are injected into the controller.
- Per-request auth uses a single `Depends(currentUserDependency.resolveCurrentUser)`.
- Controllers translate application exceptions into `HTTPException` with the appropriate status codes.

## Application exceptions at boundaries

Use cases raise intentional exceptions such as:

- `ConversationForbiddenException`
- `ConversationNotFoundException`
- `InvalidSessionException`
- `UserNotFoundException`

Presentation adapters map those to HTTP responses. Application services (for example `CurrentUserService`) do not import FastAPI. `CurrentUserDependency` is the HTTP adapter for cookie-based session resolution.

## LLM behind a port

Chat completion is not called through Semantic Kernel types from handlers.

- Port: `IChatCompletion.complete(messages: list[ChatTurn]) -> str`
- Adapter: `kernel/semantic_kernel_chat_completion.py`
- Application chat history uses `ChatTurn` DTOs, not Semantic Kernel `ChatHistory`

Semantic Kernel and Ollama remain infrastructure details.

## Data transfer objects and identity

- Request/response and query result shapes live under `data_transfer_objects/` (Pydantic models, typically frozen).
- Application-facing `User` lives under `models/` and is distinct from persistence records in `db/models/`.
- New entity identifiers use **UUIDv7** where UUIDs are generated for users/sessions.

## Configuration and migrations

- Runtime configuration is loaded through `config/settings.py` (environment / `.env`).
- Schema evolution is handled with **Alembic** under `alembic/`.
- Persistence uses PostgreSQL schemas such as `people` and `conversations`.

## Testing stance

Unit tests under `app/tests/` favour isolating application and adapter behaviour with mocks (UoW, repositories, LLM, HTTP TestClient). The goal is high coverage of backend behaviour without requiring a live database or model server for the default suite.

## Pattern index

| Pattern | Where it shows up |
| --- | --- |
| Onion / ports and adapters | Folder layout + `abstractions/` vs `db/` / `kernel/` / `controllers/` |
| Dependency inversion | Interfaces in `abstractions/`; constructors take ports |
| Constructor injection | Controllers, handlers, auth services, mediator |
| Composition root | `main.py` |
| CQRS | `commands/` + `queries/` + separate handlers |
| Mediator | `utils/mediator.py` |
| Unit of Work | `db/unit_of_work.py`, `IUnitOfWork` |
| Repository | `db/repositories/*`, matching interfaces |
| Factory | `UnitOfWorkFactory` |
| DTO | `data_transfer_objects/` |
| HTTP adapter | Controllers, `CurrentUserDependency` |
| Port for external AI | `IChatCompletion` |
| Explicit application exceptions | `exceptions/` |
