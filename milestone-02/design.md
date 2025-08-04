# Milestone 2: Design Specification

## Architecture Overview

This milestone transforms the basic AI integration from Milestone 1 into a sophisticated analysis engine with consistent scoring, actionable recommendations, and data persistence. The design emphasizes modularity, extensibility, and professional presentation suitable for legal workflow integration.

## Enhanced System Architecture

### Architectural Changes from Milestone 1

```
┌─────────────────────────────────────────────────────────────┐
│                Enhanced Streamlit Interface                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │ Text Input  │  │Score Display│  │ Analytics Dashboard     │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                Application Controller                       │
│                      (app.py)                              │
└─────────────────────────────────────────────────────────────┘
                                │
           ┌────────────────────┼────────────────────┐
           ▼                    ▼                    ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  Text Processor  │  │   AI Analyzer    │  │ Scoring Engine   │
│ (milestone-01)   │  │ (enhanced)       │  │     (new)        │
└──────────────────┘  └──────────────────┘  └──────────────────┘
                                │                    │
                                ▼                    ▼
                    ┌──────────────────┐  ┌──────────────────┐
                    │   OpenAI API     │  │Recommendation    │
                    │    Service       │  │    Engine        │
                    └──────────────────┘  └──────────────────┘
                                                     │
                                                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    Database Layer                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │  SQLite DB  │  │ Data Models │  │   Analytics Engine      │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Component Design Specifications

### 1. Enhanced AI Analyzer (`ai_analyzer.py`)

**Purpose**: Provide more structured and consistent AI analysis with detailed scoring components

**Enhanced Features**:
- Refined prompts for consistent scoring across components
- Structured JSON responses with confidence scores
- Better error handling and response validation
- Component-specific analysis depth

**Core Functions**:
```python
class NexusLetterAnalyzer:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
    
    def analyze_letter(self, letter_text: str) -> dict:
        """Enhanced analysis with component-specific evaluation"""
        
    def _build_detailed_prompt(self, text: str) -> str:
        """Construct comprehensive analysis prompt with scoring criteria"""
        
    def _validate_response(self, response: dict) -> dict:
        """Validate and clean AI response for consistency"""
        
    def get_component_analysis(self, letter_text: str, component: str) -> dict:
        """Focused analysis on specific component (medical opinion, etc.)"""
```

### 2. Scoring Engine (`scoring_engine.py`)

**Purpose**: Convert AI analysis into consistent numerical scores and decision recommendations

**Core Components**:

#### Scoring Framework
```python
class VAComplianceScorer:
    # Scoring weights for each component
    COMPONENT_WEIGHTS = {
        'medical_opinion': 0.25,      # 25 points max
        'service_connection': 0.25,   # 25 points max
        'medical_rationale': 0.25,    # 25 points max
        'professional_format': 0.25   # 25 points max
    }
    
    def calculate_component_score(self, component: str, ai_analysis: dict) -> dict:
        """Calculate score for individual component with breakdown"""
        
    def calculate_overall_score(self, component_scores: dict) -> dict:
        """Calculate final score and recommendation"""
        
    def get_score_breakdown(self, scores: dict) -> dict:
        """Provide detailed explanation of scoring"""
```

#### Scoring Criteria Implementation
```python
# Medical Opinion Component (25 points)
MEDICAL_OPINION_CRITERIA = {
    'probability_language': {
        'weight': 0.4,  # 10 points
        'keywords': ['at least as likely as not', '50% or greater', 'more probable than not'],
        'scoring': {
            'excellent': 10,  # Clear probability statement
            'good': 7,        # Implied probability  
            'fair': 4,        # Weak probability indication
            'poor': 0         # No probability language
        }
    },
    'opinion_certainty': {
        'weight': 0.4,  # 10 points
        'avoid_keywords': ['possibly', 'maybe', 'might', 'could be'],
        'prefer_keywords': ['opinion', 'conclude', 'determine'],
        'scoring': {
            'excellent': 10,  # Definitive medical opinion
            'good': 7,        # Clear opinion with minor hedging
            'fair': 4,        # Tentative opinion
            'poor': 0         # Speculation only
        }
    },
    'medical_basis': {
        'weight': 0.2,  # 5 points
        'indicators': ['examination', 'records review', 'clinical findings'],
        'scoring': {
            'excellent': 5,   # Clear medical basis stated
            'good': 3,        # Implied medical basis
            'fair': 1,        # Minimal medical basis
            'poor': 0         # No medical basis evident
        }
    }
}
```

### 3. Recommendation Engine (`recommendation_engine.py`)

**Purpose**: Generate actionable feedback and workflow recommendations based on analysis scores

**Core Functions**:
```python
class RecommendationEngine:
    # Decision thresholds
    DECISION_THRESHOLDS = {
        'auto_approve': 85,     # 85-100: Auto-approve
        'attorney_review': 70,  # 70-84: Attorney review
        'revision_required': 0  # 0-69: Revision required
    }
    
    def get_workflow_recommendation(self, overall_score: int) -> dict:
        """Determine approval pathway based on score"""
        
    def generate_improvement_recommendations(self, component_scores: dict, ai_analysis: dict) -> list:
        """Create specific, actionable improvement suggestions"""
        
    def create_client_summary(self, analysis_results: dict) -> str:
        """Generate professional summary suitable for client communication"""
        
    def prioritize_improvements(self, recommendations: list) -> list:
        """Order recommendations by impact on VA approval likelihood"""
```

#### Recommendation Templates
```python
IMPROVEMENT_TEMPLATES = {
    'medical_opinion': {
        'missing_probability': "Add explicit probability language such as 'it is at least as likely as not' or 'there is a greater than 50% probability'",
        'weak_opinion': "Strengthen medical opinion by using definitive language like 'it is my medical opinion' rather than speculative terms",
        'no_medical_basis': "Include reference to clinical examination, medical records review, or specific medical findings"
    },
    'service_connection': {
        'missing_connection': "Explicitly state the connection between military service and current condition",
        'vague_service_reference': "Provide specific details about service events, exposures, or injuries",
        'no_temporal_relationship': "Clarify the timeline between service and condition onset"
    }
    # ... additional templates for other components
}
```

### 4. Database Layer (`database.py`)

**Purpose**: Persistent storage for analysis results, review history, and analytics data

**Database Schema Design**:
```sql
-- Analysis results table
CREATE TABLE analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    letter_hash TEXT NOT NULL,  -- SHA-256 hash of letter content
    letter_length INTEGER NOT NULL,
    
    -- Overall scoring
    overall_score INTEGER NOT NULL,
    overall_recommendation TEXT NOT NULL,
    
    -- Component scores
    medical_opinion_score INTEGER NOT NULL,
    service_connection_score INTEGER NOT NULL,
    medical_rationale_score INTEGER NOT NULL,
    professional_format_score INTEGER NOT NULL,
    
    -- AI analysis data
    ai_response_json TEXT NOT NULL,  -- Full AI response for reference
    processing_time_seconds REAL NOT NULL,
    api_tokens_used INTEGER,
    
    -- Analysis metadata
    analysis_version TEXT DEFAULT 'v2.0',
    user_session TEXT,
    
    UNIQUE(letter_hash, analysis_version)  -- Prevent duplicate analysis
);

-- Recommendations table (normalized for analytics)
CREATE TABLE recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id INTEGER NOT NULL,
    component TEXT NOT NULL,  -- which component this addresses
    recommendation_type TEXT NOT NULL,  -- category of recommendation
    recommendation_text TEXT NOT NULL,
    priority_order INTEGER NOT NULL,
    
    FOREIGN KEY (analysis_id) REFERENCES analyses (id) ON DELETE CASCADE
);

-- Performance metrics table
CREATE TABLE metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    metric_name TEXT NOT NULL,
    metric_value REAL NOT NULL,
    
    UNIQUE(date, metric_name)
);
```

**Database Interface**:
```python
class AnalysisDatabase:
    def __init__(self, db_path: str = "nexus_analyzer.db"):
        self.db_path = db_path
        self.init_database()
    
    def store_analysis(self, analysis_data: dict) -> int:
        """Store complete analysis results, return analysis ID"""
        
    def get_analysis_history(self, limit: int = 50) -> list:
        """Retrieve recent analysis history with summary data"""
        
    def get_analytics_data(self, date_range: tuple = None) -> dict:
        """Calculate and return analytics metrics"""
        
    def export_data(self, format: str = 'csv') -> str:
        """Export analysis data for external analysis"""
```

### 5. Analytics Engine (`analytics.py`)

**Purpose**: Calculate performance metrics and generate insights for system effectiveness

**Core Analytics Functions**:
```python
class AnalyticsEngine:
    def __init__(self, database: AnalysisDatabase):
        self.db = database
    
    def calculate_score_distribution(self) -> dict:
        """Distribution of scores across all analyses"""
        
    def get_approval_rate_trends(self, days: int = 30) -> dict:
        """Approval recommendation trends over time"""
        
    def identify_common_issues(self) -> dict:
        """Most frequent improvement recommendations"""
        
    def calculate_processing_metrics(self) -> dict:
        """API usage, response times, success rates"""
        
    def generate_executive_summary(self) -> dict:
        """High-level system performance summary"""
```

### 6. Enhanced UI Components (Streamlit Interface)

**Purpose**: Professional presentation of scoring results and analytics

#### Scoring Display Component
```python
def display_scoring_results(analysis_results: dict):
    """Professional scoring display with visual indicators"""
    
    # Overall score with color-coded indicator
    score = analysis_results['overall_score']
    if score >= 85:
        st.success(f"🟢 Overall Score: {score}/100 - Auto-Approve Recommended")
    elif score >= 70:
        st.warning(f"🟡 Overall Score: {score}/100 - Attorney Review Recommended") 
    else:
        st.error(f"🔴 Overall Score: {score}/100 - Revision Required")
    
    # Component breakdown with progress bars
    st.subheader("Component Scores")
    components = ['Medical Opinion', 'Service Connection', 'Medical Rationale', 'Professional Format']
    for component in components:
        score_key = component.lower().replace(' ', '_') + '_score'
        component_score = analysis_results[score_key]
        st.progress(component_score / 25, text=f"{component}: {component_score}/25")
```

#### Analytics Dashboard Component
```python
def display_analytics_dashboard(analytics_data: dict):
    """Basic analytics dashboard for system monitoring"""
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Analyses", analytics_data['total_analyses'])
    with col2:
        st.metric("Average Score", f"{analytics_data['avg_score']:.1f}")
    with col3:
        st.metric("Auto-Approve Rate", f"{analytics_data['auto_approve_rate']:.1f}%")
    with col4:
        st.metric("Processing Time", f"{analytics_data['avg_processing_time']:.1f}s")
```

## Data Flow Design

### Enhanced Analysis Workflow

1. **Input Processing**: User submits nexus letter text (from Milestone 1)
2. **Text Preprocessing**: Clean and validate input (from Milestone 1)
3. **Enhanced AI Analysis**: Send to OpenAI with detailed prompts
4. **Scoring Calculation**: Process AI response through scoring engine
5. **Recommendation Generation**: Create actionable feedback based on scores
6. **Database Storage**: Persist all analysis data for tracking
7. **Results Presentation**: Display scores, recommendations, and analytics
8. **Analytics Update**: Update performance metrics in real-time

### Database Transaction Design

```python
def complete_analysis_workflow(letter_text: str) -> dict:
    """Complete analysis with atomic database operations"""
    
    try:
        # Begin database transaction
        with database.transaction():
            # Process analysis
            ai_results = ai_analyzer.analyze_letter(letter_text)
            scores = scoring_engine.calculate_scores(ai_results)
            recommendations = recommendation_engine.generate_recommendations(scores, ai_results)
            
            # Store results
            analysis_id = database.store_analysis({
                'letter_text': letter_text,
                'ai_results': ai_results,
                'scores': scores,
                'recommendations': recommendations
            })
            
            # Update analytics
            analytics.update_metrics(analysis_id)
            
            return {
                'analysis_id': analysis_id,
                'scores': scores,
                'recommendations': recommendations,
                'analytics': analytics.get_current_metrics()
            }
            
    except Exception as e:
        # Rollback transaction on any failure
        logger.error(f"Analysis workflow failed: {e}")
        raise AnalysisError("Analysis could not be completed")
```

## Performance Optimizations

### Scoring Engine Performance
- Pre-compiled regex patterns for text analysis
- Cached scoring criteria to avoid repeated calculations
- Efficient component score aggregation
- Optimized database queries with proper indexing

### Database Performance
- Strategic indexing on frequently queried fields
- Connection pooling for concurrent requests
- Efficient batch operations for analytics queries
- Data archiving strategy for long-term storage

### UI Performance
- Cached analytics calculations (refresh every 5 minutes)
- Streamlit component optimization
- Progressive loading for large datasets
- Efficient chart rendering for dashboard elements

## Security and Data Privacy

### Data Protection
- Letter content hashing for privacy (no full text storage)
- Secure handling of sensitive medical information
- Database encryption at rest (SQLite encryption extension)
- API key protection in environment variables

### Access Control
- Session-based access tracking
- Basic audit logging for compliance
- Data export restrictions and controls
- Secure deletion of sensitive data

## Testing Strategy Enhancements

### Scoring Validation
- Test suite with known letter samples and expected scores
- Consistency testing across multiple analysis runs
- Edge case testing for unusual letter formats
- Regression testing for scoring algorithm changes

### Database Testing
- Transaction integrity testing
- Performance testing with large datasets
- Data migration testing for schema changes
- Backup and recovery validation

### Integration Testing
- End-to-end workflow testing with scoring and storage
- Analytics calculation accuracy testing
- UI component testing with various score scenarios
- Cross-browser compatibility for enhanced interface

## Future Architecture Considerations

### Milestone 3 Preparation
- Enhanced UI framework ready for advanced features
- Analytics infrastructure prepared for detailed reporting
- Database schema extensible for additional metrics
- Scoring engine modular for easy enhancement

### Production Scalability
- Database migration path to PostgreSQL for larger deployments
- API rate limiting and optimization strategies
- Caching layers for improved performance
- Monitoring and alerting infrastructure hooks

This design creates a robust, professional legal analysis tool that maintains the rapid development approach while adding the sophistication required for real-world disability law practice.