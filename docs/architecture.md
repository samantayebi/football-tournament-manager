# Architecture Overview

This project follows Clean Architecture with clear boundaries between layers.

## Domain

- Pure domain models and services
- No framework or infrastructure dependencies
- Path: `src/domain/`

## Application

- Use cases and ports (interfaces)
- Depends only on the domain layer
- Path: `src/application/`

## Infrastructure

- Implementations of ports (e.g., repositories)
- Depends on application layer interfaces
- Path: `src/infrastructure/`

## API

- FastAPI routes and templates
- Orchestrates use cases
- Path: `src/api/`
