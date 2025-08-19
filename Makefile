# MockX Gateway Development Makefile
# This Makefile provides common development tasks for the library

.PHONY: help install install-dev install-poetry test test-cov lint format type-check clean build publish docs examples

# Default target
help:
	@echo "MockX Gateway Development Commands:"
	@echo ""
	@echo "Installation:"
	@echo "  install      - Install the package in development mode (pip)"
	@echo "  install-dev  - Install with development dependencies (pip)"
	@echo "  install-poetry - Install with Poetry (recommended)"
	@echo ""
	@echo "Testing:"
	@echo "  test         - Run tests"
	@echo "  test-cov     - Run tests with coverage"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint         - Run linting checks"
	@echo "  format       - Format code with ruff"
	@echo "  type-check   - Run type checking with mypy"
	@echo ""
	@echo "Build & Release:"
@echo "  clean        - Clean build artifacts"
@echo "  build        - Build the package"
@echo "  release      - Run quality checks for GitHub release"
@echo "  publish      - Build and publish to PyPI"
	@echo ""
	@echo "Documentation:"
	@echo "  docs         - Build documentation"
	@echo ""
	@echo "Examples:"
	@echo "  example      - Run the basic usage example"
	@echo "  examples     - Run all examples"

# Installation
install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

install-poetry: ## Install with Poetry (recommended)
	@echo "Installing with Poetry..."
	@echo "Note: Make sure Poetry is installed: https://python-poetry.org/docs/#installation"
	poetry install

install-pre-commit: ## Install pre-commit hooks
	pre-commit install

# Testing
test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=mockexchange_gateway --cov-report=html --cov-report=term-missing

test-integration: ## Run integration tests (requires credentials)
	@echo "Loading integration test credentials..."
	@python -c "import tests.config.load_credentials; import pytest; import sys; sys.exit(pytest.main(['tests/integration/', '--integration', '-v']))"

# Code Quality
lint:
	ruff check mockexchange_gateway/ tests/ examples/

format:
	ruff format mockexchange_gateway/ tests/ examples/
	ruff check --fix mockexchange_gateway/ tests/ examples/

type-check:
	mypy mockexchange_gateway/

pre-commit: ## Run pre-commit on all files
	pre-commit run --all-files

pre-commit-update: ## Update pre-commit hooks
	pre-commit autoupdate

# Build & Release
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

build-poetry: clean ## Build with Poetry
	poetry build

publish: build
	twine upload dist/*

publish-poetry: build-poetry ## Publish with Poetry
	poetry publish

# Documentation
docs:
	@echo "Documentation building not yet implemented"
	@echo "For now, see README.md for documentation"

# Examples
example:
	python examples/basic_usage.py

examples: ## Run all examples
	@echo "Running MockX Gateway examples..."
	@echo "1. Testing imports (no external dependencies)..."
	@python examples/test_imports.py
	@echo "\n2. Basic usage (requires MockExchange)..."
	@python examples/basic_usage.py || echo "   (MockExchange not running - expected)"
	@echo "\n3. Error handling..."
	@python examples/error_handling.py || echo "   (Some errors expected)"
	@echo "\n4. Capability checking..."
	@python examples/capability_checking.py || echo "   (Some features not supported)"
	@echo "\n5. Ticker fetching..."
	@python examples/fetch_ticker.py || echo "   (MockExchange not running - expected)"
	@echo "\n6. Order placement..."
	@python examples/place_market_order.py || echo "   (MockExchange not running - expected)"
	@echo "\n7. Order listing..."
	@python examples/list_open_orders.py || echo "   (MockExchange not running - expected)"
	@echo "\n8. Advanced balance operations..."
	@python examples/advanced_balance_operations.py || echo "   (MockExchange not running - expected)"
	@echo "\n✅ All examples completed!"

# Development workflow
dev-setup: install-dev
	@echo "Development environment setup complete!"
	@echo "Run 'make test' to verify installation"

# Quick development cycle
dev: format lint type-check test
	@echo "Development cycle complete!"

test-all: test test-integration ## Run all tests (unit + integration)

# Environment setup
env-setup:
	@echo "Setting up environment..."
	@echo "Note: This library uses constructor-based configuration"
	@echo "No .env file is needed - see examples/ for usage patterns"

# Health check
health: env-setup
	@echo "Running health checks..."
	@python -c "import mockexchange_gateway; print('✅ Import successful')"
	@python -c "from mockexchange_gateway import create_paper_gateway; print('✅ Factory import successful')"
	@echo "Health checks passed!"

# Release management
release-branch: ## Create a new release branch (interactive)
	@echo "Creating release branch..."
	@echo "Choose bump type:"
	@echo "  1) patch (0.1.0 → 0.1.1)"
	@echo "  2) minor (0.1.0 → 0.2.0)"
	@echo "  3) major (0.1.0 → 1.0.0)"
	@read -p "Enter choice (1-3): " choice; \
	case $$choice in \
		1) ./scripts/create-release-branch.sh patch ;; \
		2) ./scripts/create-release-branch.sh minor ;; \
		3) ./scripts/create-release-branch.sh major ;; \
		*) echo "Invalid choice"; exit 1 ;; \
	esac

release: ## Run quality checks for release preparation
	@echo "Running quality checks for release..."
	@echo "✅ Tests..."
	@$(MAKE) test
	@echo "✅ Linting..."
	@$(MAKE) lint
	@echo "✅ Type checking..."
	@$(MAKE) type-check
	@echo "✅ Formatting..."
	@$(MAKE) format
	@echo "✅ Building..."
	@$(MAKE) build-poetry
	@echo "🎉 All checks passed! Ready for GitHub release."
	@echo "Next steps:"
	@echo "  1. Create release on GitHub"
	@echo "  2. Use the release template"
	@echo "  3. GitHub workflow will handle the rest"

release-build: ## Build and publish release
	@echo "Building release..."
	$(MAKE) clean
	$(MAKE) build
	@echo "Release built successfully!"
	@echo "To publish: make publish"

version: ## Show current version
	@python -c "import mockexchange_gateway; print(mockexchange_gateway.__version__)"
