# Milestone 4: Production Hardening - Technical Design

## Design Overview

Milestone 4 transforms the Nexus Letter AI Analyzer into a production-hardened system suitable for legal industry deployment. The design focuses on structured data validation, PHI compliance, enterprise-grade error handling, and governance frameworks while maintaining the existing user experience and performance characteristics.

## Architecture Enhancements

### Current System Integration
The production hardening features integrate seamlessly with the existing architecture:
- **Frontend Layer**: Enhanced with configuration panels and status indicators
- **AI Integration Layer**: Wrapped with structured validation and error handling
- **Business Logic Layer**: Extended with compliance and governance capabilities
- **Data Persistence Layer**: Augmented with audit trails and secure storage

### New Architecture Components

```
┌─────────────────────────────────────────────────────────────────┐
│                    Frontend Layer (Streamlit)                   │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │
│  │ Analysis UI     │ │ Config Panel    │ │ Health Dashboard│   │
│  │ (existing)      │ │ (new)           │ │ (new)           │   │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                 Validation & Security Layer (new)               │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │
│  │ Pydantic Models │ │ PHI De-ID Engine│ │ Request Tracker │   │
│  │ Schema Validation│ │ Security Rules  │ │ Correlation IDs │   │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│            Enhanced AI Integration Layer (modified)              │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │
│  │ Prompt Manager  │ │ Circuit Breaker │ │ Response Parser │   │
│  │ (new)           │ │ (new)           │ │ (enhanced)      │   │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│             Observability & Governance Layer (new)              │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │
│  │ Structured      │ │ Health Monitor  │ │ Audit Logger    │   │
│  │ Logging         │ │ Circuit Health  │ │ Compliance Logs │   │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│               Enhanced Data Layer (modified)                     │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │
│  │ Analysis Storage│ │ Audit Tables    │ │ Config Storage  │   │
│  │ (existing)      │ │ (new)           │ │ (new)           │   │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Component Design Specifications

### 1. Structured Output Validation

#### Pydantic Models Design
```python
# models/analysis_models.py
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Literal
from enum import Enum

class ProbabilityLevel(str, Enum):
    HIGHLY_PROBABLE = "highly_probable"
    PROBABLE = "probable" 
    EQUIPOISE = "equipoise"
    UNLIKELY = "unlikely"
    INSUFFICIENT = "insufficient_evidence"

class MedicalOpinion(BaseModel):
    certainty_level: ProbabilityLevel
    medical_rationale: str = Field(min_length=50)
    physician_credentials: bool
    specialty_relevance: bool
    evidence_quality: int = Field(ge=0, le=100)

class ServiceConnection(BaseModel):
    probability_statement: ProbabilityLevel
    service_event_clarity: bool
    timeline_consistency: bool
    causal_relationship: str = Field(min_length=30)
    supporting_evidence: List[str]

class VACompliance(BaseModel):
    regulation_adherence: int = Field(ge=0, le=100)
    required_elements: List[str]
    missing_elements: List[str]
    format_compliance: bool

class NexusAnalysisResult(BaseModel):
    request_id: str
    medical_opinion: MedicalOpinion
    service_connection: ServiceConnection
    va_compliance: VACompliance
    overall_score: int = Field(ge=0, le=100)
    recommendations: List[str]
    confidence_level: float = Field(ge=0.0, le=1.0)
    
    @validator('overall_score')
    def validate_score_consistency(cls, v, values):
        # Ensure overall score aligns with component scores
        if 'medical_opinion' in values and 'va_compliance' in values:
            expected_range = (values['va_compliance'].regulation_adherence - 10,
                            values['va_compliance'].regulation_adherence + 10)
            if not (expected_range[0] <= v <= expected_range[1]):
                raise ValueError('Overall score inconsistent with components')
        return v
```

#### Validation Integration Strategy
- **Response Parsing**: Structured JSON parsing with fallback handling
- **Error Recovery**: Partial analysis results with clear validation status
- **User Feedback**: Clear indication of validation success/failure
- **Logging**: Detailed validation failure tracking for debugging

### 2. PHI Compliance & Security Engine

#### De-identification Engine Design
```python
# security/phi_deidentifier.py
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class PHIType(Enum):
    PATIENT_NAME = "patient_name"
    SSN = "social_security_number"
    MRN = "medical_record_number"
    DOB = "date_of_birth"
    PHONE = "phone_number"
    ADDRESS = "address"
    CONDITION = "medical_condition"

@dataclass
class DeidentificationRule:
    phi_type: PHIType
    pattern: str
    replacement: str
    enabled: bool = True
    sensitivity_level: int = 1  # 1=low, 2=medium, 3=high

class PHIDeidentifier:
    def __init__(self, config: Dict[str, any]):
        self.rules = self._load_rules(config)
        self.audit_log = []
    
    def deidentify_text(self, text: str, correlation_id: str) -> Tuple[str, List[str]]:
        """Returns (cleaned_text, redacted_items)"""
        cleaned_text = text
        redacted_items = []
        
        for rule in self.rules:
            if rule.enabled:
                matches = re.finditer(rule.pattern, cleaned_text, re.IGNORECASE)
                for match in matches:
                    redacted_items.append({
                        'type': rule.phi_type.value,
                        'original': match.group(),
                        'position': match.span(),
                        'correlation_id': correlation_id
                    })
                    cleaned_text = re.sub(rule.pattern, rule.replacement, 
                                        cleaned_text, flags=re.IGNORECASE)
        
        self._audit_redaction(correlation_id, redacted_items)
        return cleaned_text, redacted_items
```

#### Configurable Security Settings
- **Rule-based PHI Detection**: Regex patterns with medical context awareness
- **Sensitivity Levels**: Configurable redaction strictness (conservative/moderate/minimal)
- **Custom Rules**: Law firm specific patterns and exceptions
- **Audit Integration**: Complete redaction tracking for compliance review

### 3. Error Handling & Observability Framework

#### Structured Logging Design
```python
# monitoring/structured_logger.py
import logging
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from contextlib import contextmanager

class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.correlation_context = {}
    
    @contextmanager
    def correlation_context(self, **context):
        """Context manager for request correlation"""
        old_context = self.correlation_context.copy()
        self.correlation_context.update(context)
        try:
            yield
        finally:
            self.correlation_context = old_context
    
    def log_analysis_start(self, request_id: str, text_length: int):
        self._log('info', 'analysis_started', {
            'request_id': request_id,
            'text_length': text_length,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    def log_ai_request(self, request_id: str, prompt_version: str, 
                      token_count: int, model: str):
        self._log('info', 'ai_request', {
            'request_id': request_id,
            'prompt_version': prompt_version,
            'token_count': token_count,
            'model': model,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    def log_validation_error(self, request_id: str, error_type: str, 
                           field_errors: List[str]):
        self._log('warning', 'validation_error', {
            'request_id': request_id,
            'error_type': error_type,
            'field_errors': field_errors,
            'timestamp': datetime.utcnow().isoformat()
        })
```

#### Circuit Breaker Implementation
```python
# monitoring/circuit_breaker.py
import time
from enum import Enum
from typing import Callable, Any, Optional
from dataclasses import dataclass

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, requests blocked
    HALF_OPEN = "half_open" # Testing if service recovered

@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5
    recovery_timeout: int = 60  # seconds
    success_threshold: int = 3  # for half-open -> closed

class CircuitBreaker:
    def __init__(self, config: CircuitBreakerConfig, logger: StructuredLogger):
        self.config = config
        self.logger = logger
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.config.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                self.logger.log_circuit_breaker('half_open_attempt')
            else:
                raise CircuitBreakerOpenError("Circuit breaker is open")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure(e)
            raise
```

### 4. Prompt Governance System

#### Centralized Prompt Management
```python
# prompts/prompt_manager.py
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass
import hashlib

@dataclass
class PromptVersion:
    version: str
    content: str
    created_date: str
    description: str
    va_rubrics: List[str]
    hash: str

class PromptManager:
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.prompts = self._load_prompts()
        self.active_versions = {}
    
    def get_prompt(self, prompt_type: str, version: Optional[str] = None) -> str:
        """Get prompt by type and version (latest if not specified)"""
        if prompt_type not in self.prompts:
            raise ValueError(f"Unknown prompt type: {prompt_type}")
        
        versions = self.prompts[prompt_type]
        if version is None:
            version = max(versions.keys())  # Latest version
        
        if version not in versions:
            raise ValueError(f"Version {version} not found for {prompt_type}")
        
        return versions[version].content
    
    def validate_prompt_requirements(self, prompt_type: str, version: str) -> List[str]:
        """Validate prompt contains required VA elements"""
        prompt_version = self.prompts[prompt_type][version]
        missing_elements = []
        
        required_elements = [
            "medical opinion",
            "probability language", 
            "service connection",
            "physician credentials",
            "medical rationale"
        ]
        
        for element in required_elements:
            if element not in prompt_version.content.lower():
                missing_elements.append(element)
        
        return missing_elements
```

#### Prompt Configuration Structure
```yaml
# config/prompts.yaml
nexus_analysis:
  v1.0:
    content: |
      Analyze this VA nexus letter for compliance with VA regulations...
      
      Required Analysis Components:
      1. Medical Opinion Certainty (highly probable, probable, equipoise, unlikely)
      2. Service Connection Evidence
      3. Physician Credentials Verification
      4. VA Regulation Compliance (38 CFR 3.159)
      
      Return structured JSON with required fields...
    created_date: "2024-01-15"
    description: "Initial production prompt with VA compliance rubrics"
    va_rubrics:
      - "38 CFR 3.159 - Medical evidence requirements"
      - "Medical probability standards"
      - "Service connection nexus requirements"
  
  v1.1:
    content: |
      Enhanced version with additional PHI considerations...
    created_date: "2024-01-20"
    description: "Added PHI awareness and security considerations"
    va_rubrics:
      - "38 CFR 3.159 - Medical evidence requirements"
      - "Medical probability standards" 
      - "Service connection nexus requirements"
      - "HIPAA compliance considerations"
```

## Database Schema Enhancements

### New Tables for Production Features

```sql
-- Audit and compliance tracking
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    correlation_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    event_data JSON,
    phi_redacted BOOLEAN DEFAULT FALSE,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_context TEXT
);

-- Request tracking and correlation
CREATE TABLE request_tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    correlation_id TEXT UNIQUE NOT NULL,
    request_start DATETIME NOT NULL,
    request_end DATETIME,
    analysis_id INTEGER,
    status TEXT NOT NULL, -- 'started', 'completed', 'failed'
    error_details JSON,
    performance_metrics JSON,
    FOREIGN KEY (analysis_id) REFERENCES nexus_analyses(id)
);

-- Configuration management
CREATE TABLE system_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_key TEXT UNIQUE NOT NULL,
    config_value JSON NOT NULL,
    config_type TEXT NOT NULL, -- 'phi', 'monitoring', 'prompts'
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Circuit breaker state tracking  
CREATE TABLE circuit_breaker_state (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_name TEXT UNIQUE NOT NULL,
    state TEXT NOT NULL, -- 'closed', 'open', 'half_open'
    failure_count INTEGER DEFAULT 0,
    last_failure DATETIME,
    last_success DATETIME,
    updated_date DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Prompt version tracking
CREATE TABLE prompt_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt_type TEXT NOT NULL,
    version TEXT NOT NULL,
    content TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    va_rubrics JSON,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT FALSE,
    UNIQUE(prompt_type, version)
);
```

## Configuration Management Design

### Hierarchical Configuration Structure
```yaml
# config/production.yaml
compliance:
  phi_deidentification:
    enabled: true
    sensitivity_level: 2  # 1=minimal, 2=moderate, 3=strict
    custom_rules:
      - type: "patient_name"
        pattern: "\\b[A-Z][a-z]+ [A-Z][a-z]+\\b"
        replacement: "[PATIENT_NAME]"
        enabled: true
    audit_redaction: true
    
  data_retention:
    analysis_results: 2555  # days (7 years)
    audit_logs: 2555
    phi_data: 0  # immediate deletion
    request_tracking: 365

monitoring:
  structured_logging:
    enabled: true
    level: "INFO"
    include_request_body: false  # PHI safety
    correlation_tracking: true
    
  circuit_breaker:
    openai_api:
      failure_threshold: 5
      recovery_timeout: 60
      success_threshold: 3
    database:
      failure_threshold: 3
      recovery_timeout: 30
      success_threshold: 2

ai_services:
  openai:
    model: "gpt-4"
    temperature: 0.1
    max_tokens: 2000
    timeout: 30
  
  azure_openai:  # Optional enterprise deployment
    enabled: false
    endpoint: "${AZURE_OPENAI_ENDPOINT}"
    api_key: "${AZURE_OPENAI_KEY}"
    deployment_name: "gpt-4-deployment"
    
governance:
  prompt_management:
    version_control: true
    testing_required: true
    approval_workflow: false  # Future enhancement
    
  quality_assurance:
    validation_required: true
    confidence_threshold: 0.8
    manual_review_threshold: 60  # scores below this require review
```

## Performance Considerations

### Validation Performance Impact
- **Pydantic Validation**: < 50ms additional processing time
- **PHI De-identification**: < 200ms for typical nexus letter (2-3 pages)
- **Structured Logging**: < 10ms per log entry
- **Circuit Breaker**: < 1ms overhead per protected call

### Memory Usage Optimization
- **Request Context**: Limited lifetime correlation data
- **Audit Logs**: Configurable retention with automatic cleanup
- **Validation Models**: Cached and reused across requests
- **PHI Rules**: Compiled regex patterns cached in memory

### Database Performance
- **Indexed Queries**: All correlation_id and timestamp lookups
- **Batch Operations**: Audit log insertions batched for performance
- **Connection Pooling**: Efficient database connection management
- **Query Optimization**: Prepared statements for frequent operations

## Security Architecture

### Defense in Depth Strategy
1. **Input Validation**: All user inputs validated and sanitized
2. **PHI Protection**: Multi-layer redaction and secure storage
3. **Access Control**: Configuration-based permission management
4. **Audit Trails**: Complete activity logging for compliance
5. **Secure Communication**: HTTPS for all API communications
6. **Data Encryption**: Sensitive data encrypted at rest

### Threat Modeling Results
- **PHI Exposure**: Mitigated through automated redaction
- **API Key Compromise**: Environment variable isolation
- **SQL Injection**: Parameterized queries throughout
- **Log Injection**: Structured logging with safe serialization
- **Data Breaches**: Encrypted storage and minimal retention

## Integration Points

### Existing System Integration
- **Streamlit UI**: Enhanced with configuration panels and status indicators
- **OpenAI Integration**: Wrapped with validation and circuit breaking
- **Database Layer**: Extended with audit tables and secure storage
- **Analytics Dashboard**: Enhanced with compliance and health metrics

### Third-party Service Integration
- **Azure OpenAI**: Optional enterprise-grade AI service
- **External Monitoring**: Health check endpoints for external monitoring
- **Compliance Systems**: Audit log export for external compliance tools
- **Backup Services**: Database backup integration points

This design provides a comprehensive production hardening framework that maintains system usability while adding enterprise-grade reliability, security, and governance capabilities essential for legal industry deployment.