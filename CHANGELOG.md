# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Future enhancements will be documented here

### Changed
- Future changes will be documented here

### Fixed
- Future fixes will be documented here

## [0.2.0] - 2025-08-19

### Added
- **CCXT-compatible facade** as the public API (method names & return shapes aligned with CCXT)
- **Dual backend support**:
  - Paper mode: routes to MockExchange for simulated execution
  - Production mode: routes to real exchanges via CCXT
- **ExchangeFactory** to construct the correct gateway for paper or production with a single switch
- **Capability map** (`exchange.has`) to explicitly advertise supported features per mode
- **CCXT-style error mapping** (e.g., NotSupported, InvalidOrder, InsufficientFunds, ExchangeError)
- **Adapters layer**:
  - Paper adapter (MockExchange)
  - Prod adapter (CCXT)
- **Documentation & examples**:
  - Architecture overview and capability matrix
  - Paper vs. production usage examples
  - Best-practices guidance for using MockX Gateway at the execution boundary and CCXT for data-heavy reads
- **Tooling & packaging**:
  - Poetry project configuration (with lockfile)
  - Pre-commit hooks (ruff, mypy, isort, bandit)
  - Basic CI workflow for lint/type/unit tests

### Changed
- **Repository structure** reorganized into `core/` (facade, capabilities, errors), `adapters/` (paper/prod), and `runtime/` (factory) for clearer separation of concerns
- **API surface** standardized to a stricter CCXT dialect (consistent keys/types across backends)

### Removed
- **Monolithic client layout** from 0.1.0 in favor of facade + adapters architecture
- **Pydantic dependency**, replaced by lighter validation to keep the gateway lean

## [0.1.0] - 2025-07-18

### Added
- Initial MockExchange client with a basic CCXT-like interface (tickers, balances, orders, dry-run)
- Requests-based HTTP client
- Simple error handling
- In-memory backend for tests

---

## Version History Summary

- **0.1.0**: First working MockExchange client with CCXT-like basics
- **0.2.0**: Major architectural upgrade: CCXT-compatible facade, dual backends (paper/prod), capability map, error mapping, adapters, docs, and modern tooling

---

**MockX Gateway** - A production-ready CCXT-compatible gateway for seamless switching between MockExchange and real exchanges.
