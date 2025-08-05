# Nexus Letter AI Analyzer - Production Deployment Guide

This guide covers deploying the Nexus Letter AI Analyzer using Docker and CI/CD automation.

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- OpenAI API key
- Git (for CI/CD)

### Environment Setup
1. Copy your OpenAI API key:
```bash
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

2. Choose your deployment mode:

**Development Mode:**
```bash
docker-compose --profile dev up -d
```
Access at: http://localhost:8501

**Production Mode:**
```bash
docker-compose --profile prod up -d  
```
Access at: http://localhost:80

**Run Tests:**
```bash
docker-compose --profile test run --rm nexus-test-runner
```

## File Overview

### Core Production Files

- **`Dockerfile`**: Multi-stage build with security best practices
- **`docker-compose.yml`**: Development, production, and testing configurations
- **`requirements.txt`**: Locked dependency versions for reproducible builds
- **`.dockerignore`**: Excludes unnecessary files from Docker builds
- **`health_check.py`**: Custom health monitoring for containers
- **`.github/workflows/ci.yml`**: Complete CI/CD pipeline

### Security Features

- ✅ **Non-root user execution**
- ✅ **Minimal Alpine Linux base image**
- ✅ **Multi-stage build** (reduces attack surface)
- ✅ **Dependency security scanning** (Trivy + Bandit)
- ✅ **Locked dependency versions**
- ✅ **Health monitoring** with custom checks

## CI/CD Pipeline

The GitHub Actions workflow automatically:

1. **Code Quality Checks**
   - Black formatting validation
   - Flake8 linting 
   - MyPy type checking
   - Bandit security scanning

2. **Test Execution**
   - PHI Compliance tests
   - Error Handling tests  
   - Observability tests
   - Parallel execution for speed

3. **Docker Operations**
   - Multi-platform builds (AMD64, ARM64)
   - Security scanning with Trivy
   - Integration testing
   - Container registry publishing

4. **Deployment**
   - Automatic staging deployment on main branch
   - Pull request validation
   - Test result reporting

### Setting Up CI/CD

1. **Repository Secrets** (GitHub Settings → Secrets):
```
OPENAI_API_KEY: your-openai-api-key
```

2. **Branch Protection** (recommended):
   - Require status checks: ✅ Code Quality, ✅ Test Suites, ✅ Docker Build
   - Require up-to-date branches before merging
   - Include administrators in restrictions

## Production Deployment Options

### Option 1: Docker Compose (Recommended for single server)

```bash
# Production deployment
docker-compose --profile prod up -d

# View logs
docker-compose logs -f nexus-analyzer-prod

# Update application
git pull
docker-compose --profile prod build
docker-compose --profile prod up -d
```

### Option 2: Kubernetes (Enterprise)

```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nexus-analyzer
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nexus-analyzer
  template:
    metadata:
      labels:
        app: nexus-analyzer
    spec:
      containers:
      - name: nexus-analyzer
        image: ghcr.io/your-org/nexus-letter-analyzer:latest
        ports:
        - containerPort: 8501
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: nexus-secrets
              key: openai-api-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          exec:
            command:
            - python
            - health_check.py
          initialDelaySeconds: 60
          periodSeconds: 30
```

### Option 3: Cloud Platforms

**AWS ECS:**
```json
{
  "family": "nexus-analyzer",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "nexus-analyzer",
      "image": "ghcr.io/your-org/nexus-letter-analyzer:latest",
      "portMappings": [
        {
          "containerPort": 8501,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "OPENAI_API_KEY",
          "value": "your-api-key"
        }
      ],
      "healthCheck": {
        "command": ["CMD-SHELL", "python health_check.py"],
        "interval": 30,
        "timeout": 10,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
```

## Monitoring and Observability

### Health Monitoring
```bash
# Check container health
docker ps

# View health check logs
docker inspect nexus-analyzer-prod | grep -A 10 Health

# Manual health check
docker exec nexus-analyzer-prod python health_check.py
```

### Application Logs
```bash
# View application logs
docker-compose logs -f nexus-analyzer-prod

# Access structured logs
docker exec nexus-analyzer-prod ls -la logs/
```

### Performance Monitoring
The application includes built-in observability:
- Structured logging with correlation IDs
- Performance metrics collection
- Error tracking and circuit breaker patterns
- PHI compliance auditing

## Security Considerations

### Container Security
- Runs as non-root user (UID 1001)
- Minimal base image (Alpine Linux)
- No unnecessary packages or tools
- Read-only root filesystem (optional)

### Application Security  
- PHI data protection and scrubbing
- Input validation and sanitization
- Rate limiting and circuit breakers
- Secure secret management

### Network Security
```yaml
# docker-compose.yml security additions
services:
  nexus-analyzer-prod:
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp:noexec,nosuid,size=100m
    cap_drop:
      - ALL
    cap_add:
      - CHOWN
      - DAC_OVERRIDE
      - SETGID
      - SETUID
```

## Troubleshooting

### Common Issues

**Container won't start:**
```bash
# Check logs
docker-compose logs nexus-analyzer-prod

# Verify environment
docker-compose config

# Test health check manually
docker run --rm -it nexus-analyzer python health_check.py
```

**API connectivity issues:**
```bash
# Test OpenAI API key
docker exec nexus-analyzer-prod python -c "
import openai
import os
openai.api_key = os.getenv('OPENAI_API_KEY')
print('API key configured:', bool(openai.api_key))
"
```

**Performance issues:**
```bash
# Monitor resource usage
docker stats nexus-analyzer-prod

# Check application metrics
docker exec nexus-analyzer-prod python -c "
from observability import create_performance_monitor
monitor = create_performance_monitor('health_check')
print(monitor.get_metrics())
"
```

### Log Analysis
```bash
# Filter error logs
docker-compose logs nexus-analyzer-prod | grep ERROR

# Monitor PHI compliance
docker exec nexus-analyzer-prod grep "PHI_DETECTED" logs/*.log

# Performance analysis
docker exec nexus-analyzer-prod grep "PERFORMANCE" logs/*.log
```

## Development Workflow

### Local Development
```bash
# Development with live reload
docker-compose --profile dev up

# Run specific tests
docker-compose --profile test run --rm nexus-test-runner python test_phi_compliance.py

# Interactive debugging
docker-compose --profile dev exec nexus-analyzer-dev /bin/sh
```

### Testing Strategy
```bash
# Run all test suites
make test-all

# Individual test suites
make test-phi          # PHI compliance
make test-error        # Error handling  
make test-observability # Monitoring

# Security scan
make security-scan
```

## Production Checklist

Before deploying to production:

- [ ] ✅ Set strong, unique OpenAI API key
- [ ] ✅ Configure proper resource limits
- [ ] ✅ Set up log aggregation and monitoring
- [ ] ✅ Configure backup strategy for persistent data
- [ ] ✅ Implement SSL/TLS termination (load balancer)
- [ ] ✅ Set up automated security updates
- [ ] ✅ Configure alerting for health check failures
- [ ] ✅ Test disaster recovery procedures
- [ ] ✅ Review and approve security scan results
- [ ] ✅ Validate PHI compliance requirements

## Support and Maintenance

### Updates
```bash
# Update to latest version
git pull origin main
docker-compose --profile prod pull
docker-compose --profile prod up -d
```

### Backup Data
```bash
# Backup persistent volumes
docker run --rm -v nexus-data:/data -v $(pwd):/backup alpine tar czf /backup/nexus-data-backup.tar.gz -C /data .
```

### Scale Production
```bash
# Scale horizontally (multiple instances)
docker-compose --profile prod up -d --scale nexus-analyzer-prod=3

# Use load balancer for distribution
# Configure external load balancer to distribute traffic
```

For additional support or questions about production deployment, refer to the project documentation or create an issue.