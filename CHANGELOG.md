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
- **Complete Architecture Overhaul**: New clean, modular design
- **CCXT-Compatible Facade**: Drop-in replacement for CCXT
- **Dual Mode Support**: Paper (MockExchange) and Production (CCXT) modes
- **Environment-Based Configuration**: Automatic mode switching via environment variables
- **Capability System**: Explicit feature detection via `exchange.has` dict
- **Fail-Fast Error Handling**: Clear `NotSupported` errors for unsupported features
- **Type Safety**: Full type hints and validation throughout
- **Poetry support** - Added Poetry as the recommended package manager with full pip compatibility
- **Lock file** - `poetry.lock` for reproducible builds and dependency resolution
- **Enhanced Makefile** - Added Poetry commands alongside pip commands (`build-poetry`, `publish-poetry`, etc.)
- **Table of Contents** - Added comprehensive TOC to README for better navigation
- **MockExchange API documentation** - Detailed explanation of API behavior differences and compatibility
- **GitHub installation instructions** - Clear instructions for installing from GitHub repository
- **MockExchange-specific features** - `fetch_balance(asset)`, `fetch_balance_list()`, `deposit()`, `withdraw()`, `can_execute_order()`
- **Enhanced examples** - New examples for error handling, capability checking, ticker analysis, and balance operations
- **Examples README** - Comprehensive guide to all example files and their usage
- **Pre-commit hooks** - Automated code quality checks with ruff, mypy, bandit, isort, and commitizen
- **GitHub Actions CI/CD** - Automated testing, linting, and release workflows
- **Integration test framework** - Pytest markers and credential management for integration testing
- **Comprehensive documentation** - Enhanced README with detailed API compatibility explanations
- **Security scanning** - Bandit security analysis integrated into pre-commit hooks

#### Core Components
- **Configuration Management** (`config/`)
  - Environment variable handling (`env.py`)
  - Symbol mapping and normalization (`symbols.py`)
- **Core Functionality** (`core/`)
  - CCXT-compatible facade (`facade.py`)
  - Error classes matching CCXT (`errors.py`)
  - Capability detection (`capabilities.py`)
- **Backend Adapters** (`adapters/`)
  - Paper adapter for MockExchange (`paper.py`)
  - Production adapter for CCXT (`prod.py`)
  - Data format conversion (`mapping.py`)
- **Runtime Components** (`runtime/`)
  - Gateway factory (`factory.py`)

#### Factory Functions
- `create_gateway()` - Environment-based gateway creation
- `create_paper_gateway()` - Direct MockExchange gateway
- `create_prod_gateway()` - Direct CCXT gateway

#### Error Classes
- `MockXError` - Base exception class
- `ExchangeError` - Exchange-related errors
- `AuthenticationError` - Authentication failures
- `BadRequest` - Invalid requests
- `InsufficientFunds` - Insufficient balance
- `InvalidOrder` - Order-related errors
- `NotSupported` - Unsupported features
- `NetworkError` - Network-related errors

#### Capabilities
- **Paper Mode**: Core trading features (orders, balance, tickers)
- **Production Mode**: Full CCXT feature set
- **Capability Detection**: `gateway.has` dict for feature checking

### Changed
- **Package Structure**: Complete reorganization for better modularity
- **API Design**: CCXT-compatible interface throughout
- **Configuration**: Environment-based instead of hardcoded values
- **Error Handling**: CCXT-style error hierarchy
- **Type Safety**: Comprehensive type hints and validation
- **Package management** - Migrated from setuptools to Poetry while maintaining pip compatibility
- **Build system** - Updated to use `poetry-core` as build backend
- **fetchTickers implementation** - Refactored to handle MockExchange's unique API behavior (list vs. ticker data)
- **fetchTickers behavior** - Removed arbitrary 50-ticker limit to match CCXT behavior exactly
- **fetch_open_orders implementation** - Fixed to properly filter MockExchange order statuses (`new`, `partially_filled`)
- **MyPy configuration** - Optimized for external API integration with proper ignore settings
- **Constructor-based configuration** - Refactored from environment variables to explicit parameters
- **Code formatting** - Applied Ruff formatting across entire codebase
- **Error handling** - Improved exception specificity in paper adapter
- **Documentation structure** - Enhanced with proper sections, examples, and navigation

### Fixed
- **Linting issues** - Resolved unused imports and f-string formatting issues
- **Type checking** - Fixed MyPy configuration for CCXT compatibility
- **Security issues** - Resolved Bandit warnings with specific exception handling
- **Order status mapping** - Corrected MockExchange order status filtering
- **API compatibility** - Ensured full CCXT method signature compliance

### Removed
- Old monolithic client structure
- Hardcoded configuration values
- Pydantic dependency (simplified data handling)
- **Environment variable dependencies** - Removed from library instantiation (still used for integration tests)
- **Artificial limits** - Removed 50-ticker limit from fetchTickers
- **Hardcoded URLs** - Replaced personal MockExchange URL with localhost default

## [0.1.0] - 2025-07-18

### Added
- Initial implementation of MockExchange client
- Basic CCXT-like interface
- HTTP client for MockExchange API
- Support for basic operations:
  - Market data (tickers)
  - Balance snapshots
  - Order lifecycle (create, list, cancel)
  - Dry-run order execution
- Pydantic models for data validation
- Basic error handling
- In-memory backend for testing
- Protocol definitions for CCXT compatibility

### Features
- `load_markets()` - Populate symbol cache
- `fetch_ticker()` - Get single ticker
- `fetch_tickers()` - Get all tickers
- `fetch_balance()` - Get account balance
- `create_order()` - Create market/limit orders
- `fetch_order()` - Get specific order
- `fetch_orders()` - List orders with filtering
- `fetch_open_orders()` - Get open orders
- `cancel_order()` - Cancel orders
- `can_execute_order()` - Dry-run order validation

### Technical Details
- Python 3.11+ support
- Requests-based HTTP client
- Pydantic for data validation
- Type hints throughout
- Basic test suite
- Development dependencies setup

---

## Version History Summary

- **0.1.0**: Initial implementation with basic MockExchange client
- **0.2.0**: Complete architecture overhaul with CCXT compatibility, dual-mode support, Poetry migration, comprehensive documentation, enhanced tooling, and production-ready polish

---

**MockX Gateway** - A production-ready CCXT-compatible gateway for seamless switching between MockExchange and real exchanges.
