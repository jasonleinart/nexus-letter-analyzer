# Nexus Letter AI Analyzer - Production Makefile
# Provides convenient commands for development, testing, and deployment

.PHONY: help dev prod test clean build security-scan format lint type-check install

# Default target
help:
	@echo "Nexus Letter AI Analyzer - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  dev                 Start development environment"
	@echo "  install             Install Python dependencies locally"
	@echo "  format              Format code with Black"
	@echo "  lint                Run linting with flake8"
	@echo "  type-check          Run type checking with mypy"
	@echo ""
	@echo "Testing:"
	@echo "  test-all            Run all test suites"
	@echo "  test-phi            Run PHI compliance tests"
	@echo "  test-error          Run error handling tests"
	@echo "  test-observability  Run observability tests"
	@echo "  test-integration    Run integration tests with Docker"
	@echo ""
	@echo "Production:"
	@echo "  prod                Start production environment"
	@echo "  build               Build Docker images"
	@echo "  security-scan       Run security scans"
	@echo "  deploy-staging      Deploy to staging environment"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean               Remove containers and images"
	@echo "  logs                View production logs"
	@echo "  health              Check system health"
	@echo "  backup              Backup production data"

# Development commands
dev:
	@echo "Starting development environment..."
	docker-compose --profile dev up -d
	@echo "Development server available at: http://localhost:8501"

install:
	@echo "Installing Python dependencies locally..."
	pip install -r requirements.txt

format:
	@echo "Formatting code with Black..."
	black .

lint:
	@echo "Running linting with flake8..."
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

type-check:
	@echo "Running type checking with mypy..."
	mypy . --ignore-missing-imports --no-strict-optional

# Testing commands
test-all: test-phi test-error test-observability
	@echo "All test suites completed!"

test-phi:
	@echo "Running PHI compliance tests..."
	docker-compose --profile test run --rm nexus-test-runner python test_phi_compliance.py

test-error:
	@echo "Running error handling tests..."
	docker-compose --profile test run --rm nexus-test-runner python test_error_handling.py

test-observability:
	@echo "Running observability tests..."
	docker-compose --profile test run --rm nexus-test-runner python test_observability_comprehensive.py

test-integration:
	@echo "Running integration tests with Docker..."
	docker-compose --profile test run --rm nexus-test-runner

# Production commands
prod:
	@echo "Starting production environment..."
	docker-compose --profile prod up -d
	@echo "Production server available at: http://localhost:80"

build:
	@echo "Building Docker images..."
	docker-compose build
	@echo "Docker images built successfully!"

security-scan:
	@echo "Running security scans..."
	@echo "1. Building image for scanning..."
	docker build -t nexus-security-scan .
	@echo "2. Running Trivy security scan..."
	docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
		-v $$(pwd):/workspace aquasec/trivy:latest \
		image nexus-security-scan
	@echo "3. Running Bandit security scan..."
	docker run --rm -v $$(pwd):/workspace nexus-security-scan \
		bandit -r /workspace -f json -o /workspace/bandit-report.json || true
	@echo "Security scans completed!"

deploy-staging:
	@echo "Deploying to staging environment..."
	@echo "Note: Configure your staging deployment commands here"
	# Add your staging deployment commands
	# docker-compose -f docker-compose.staging.yml up -d
	# kubectl apply -f kubernetes/
	# etc.

# Maintenance commands
clean:
	@echo "Cleaning up containers and images..."
	docker-compose down --volumes --remove-orphans
	docker system prune -f
	@echo "Cleanup completed!"

logs:
	@echo "Viewing production logs..."
	docker-compose --profile prod logs -f nexus-analyzer-prod

health:
	@echo "Checking system health..."
	@echo "Container status:"
	docker-compose --profile prod ps
	@echo ""
	@echo "Application health check:"
	docker-compose --profile prod exec nexus-analyzer-prod python health_check.py || echo "Health check failed"

backup:
	@echo "Creating backup of production data..."
	@mkdir -p backups
	docker run --rm \
		-v nexus-data:/data \
		-v $$(pwd)/backups:/backup \
		alpine tar czf /backup/nexus-data-backup-$$(date +%Y%m%d-%H%M%S).tar.gz -C /data .
	@echo "Backup completed in backups/ directory"

# Quality assurance
qa: format lint type-check test-all security-scan
	@echo "Quality assurance checks completed!"

# CI simulation
ci: qa build test-integration
	@echo "CI pipeline simulation completed!"

# Development setup
setup: install
	@echo "Setting up development environment..."
	@if [ ! -f .env ]; then \
		echo "Creating .env file template..."; \
		echo "OPENAI_API_KEY=your-api-key-here" > .env; \
		echo "Please edit .env file with your actual API key"; \
	fi
	@mkdir -p data logs test_logs
	@echo "Development setup completed!"
	@echo "Next steps:"
	@echo "1. Edit .env file with your OpenAI API key"
	@echo "2. Run 'make dev' to start development server"