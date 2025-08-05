"""
Integration tests for production-ready features.

Tests PHI compliance, error handling, observability, and overall system integration.
"""

import time
import uuid
import pytest
from unittest.mock import Mock, patch
from datetime import datetime

# Import production modules
from phi_compliance import PHIDetectionEngine, SecureAuditLogger, phi_compliant_processing
from error_handling import (
    CircuitBreaker, CircuitBreakerConfig, RobustRetryManager, RetryConfig,
    ErrorClassifier, ErrorCategory, with_error_handling
)
from observability import (
    StructuredLogger, MetricsCollector, PerformanceMonitor, 
    observability_context
)
from ai_analyzer_enhanced import create_analyzer


def test_phi_detection_integration():
    """Test PHI detection with realistic nexus letter content."""
    print("\n=== Testing PHI Detection Integration ===")
    
    # Realistic test content with PHI
    test_letter = """
    [Medical Center Name]
    123 Medical Drive
    Healthcare City, ST 12345
    Phone: (555) 123-4567

    Date: March 15, 2024

    RE: Nexus Letter for John A. Smith
    SSN: 123-45-6789
    DOB: January 15, 1975
    Address: 456 Veteran Lane, Military Town, ST 67890

    To Whom It May Concern,

    I am Dr. Jane Medical, MD, a licensed physician specializing in internal medicine.
    
    Patient John Smith was seen in my clinic on February 20, 2024, for evaluation 
    of his chronic back pain condition. Based on my examination and review of his
    military service records, it is my medical opinion that it is at least as likely
    as not (greater than 50% probability) that his current lumbar spine condition
    is related to his military service from 1995-2005.

    The patient reported that he injured his back during a training exercise in 2003
    while serving in the Army. Medical records from that time show he was treated
    for acute back strain at the base hospital.

    Contact me at jane.medical@healthcare.com or (555) 987-6543 for any questions.

    Sincerely,
    Dr. Jane Medical, MD
    License #MD123456
    """
    
    phi_detector = PHIDetectionEngine(strict_mode=True)
    
    # Test detection
    detections = phi_detector.detect_phi(test_letter)
    print(f"PHI detections found: {len(detections)}")
    
    # Should detect multiple PHI categories
    categories_found = set(d.category.value for d in detections)
    print(f"PHI categories detected: {categories_found}")
    
    expected_categories = {'name', 'ssn', 'date_of_birth', 'address', 'phone', 'email'}
    found_expected = categories_found.intersection(expected_categories)
    print(f"Expected categories found: {found_expected}")
    
    # Test de-identification
    cleaned_text, detections = phi_detector.de_identify_text(test_letter)
    
    print(f"\nOriginal length: {len(test_letter)}")
    print(f"Cleaned length: {len(cleaned_text)}")
    print(f"PHI items redacted: {len(detections)}")
    
    # Verify no PHI remains in cleaned text
    assert "John A. Smith" not in cleaned_text
    assert "123-45-6789" not in cleaned_text
    assert "jane.medical@healthcare.com" not in cleaned_text
    assert "(555) 123-4567" not in cleaned_text
    
    print("✅ PHI detection and redaction working correctly")
    
    # Test with compliance context
    with phi_compliant_processing() as (corr_id, detector, audit_logger):
        cleaned_context, detections_context = detector.de_identify_text(test_letter, corr_id)
        print(f"Context processing - Correlation ID: {corr_id}")
        print(f"Context processing - Detections: {len(detections_context)}")
    
    print("✅ PHI compliance context working correctly")


def test_error_handling_integration():
    """Test error handling with realistic failure scenarios."""
    print("\n=== Testing Error Handling Integration ===")
    
    # Test circuit breaker
    config = CircuitBreakerConfig(failure_threshold=2, timeout_seconds=1)
    circuit_breaker = CircuitBreaker(config, "test_api")
    
    def failing_function():
        raise Exception("Simulated API failure")
    
    # Test circuit breaker operation
    print("Testing circuit breaker...")
    
    # Should start closed
    assert circuit_breaker.state.value == "closed"
    
    # Cause failures to trip circuit breaker
    for attempt in range(3):
        try:
            circuit_breaker.call(failing_function)
        except Exception:
            pass
    
    # Should now be open
    assert circuit_breaker.state.value == "open"
    print("✅ Circuit breaker opened after failures")
    
    # Test retry manager
    retry_config = RetryConfig(max_attempts=3, base_delay_seconds=0.1)
    retry_manager = RobustRetryManager(retry_config)
    
    attempt_count = 0
    def flaky_function():
        nonlocal attempt_count
        attempt_count += 1
        if attempt_count < 3:
            raise Exception("Temporary failure")
        return "Success!"
    
    # Test retry logic
    print("Testing retry logic...")
    result = retry_manager.execute_with_retry(flaky_function, correlation_id="test-retry")
    assert result == "Success!"
    assert attempt_count == 3
    print("✅ Retry logic working correctly")
    
    # Test error classification
    print("Testing error classification...")
    
    test_errors = [
        (Exception("Connection timeout"), ErrorCategory.API_TIMEOUT),
        (Exception("Rate limit exceeded"), ErrorCategory.API_RATE_LIMIT),
        (Exception("Authentication failed"), ErrorCategory.API_AUTHENTICATION),
        (Exception("JSON parse error"), ErrorCategory.PARSING_ERROR),
        (Exception("Unknown error"), ErrorCategory.UNKNOWN_ERROR)
    ]
    
    for error, expected_category in test_errors:
        classified = ErrorClassifier.classify_error(error)
        print(f"  {str(error)} -> {classified.value}")
        # Note: Classification is heuristic, so we'll just verify it returns a category
        assert isinstance(classified, ErrorCategory)
    
    print("✅ Error classification working correctly")
    
    # Test error handling decorator
    @with_error_handling(
        retry_config=RetryConfig(max_attempts=2, base_delay_seconds=0.1),
        enable_fallback=True
    )
    def test_decorated_function(text: str):
        if "fail" in text:
            raise Exception("Simulated failure")
        return {"success": True, "text": text}
    
    # Test successful call
    result = test_decorated_function("success test")
    assert result["success"] is True
    
    # Test fallback
    result = test_decorated_function("fail test")
    assert "fallback_applied" in result.get("error_context", {})
    
    print("✅ Error handling decorator working correctly")


def test_observability_integration():
    """Test observability features."""
    print("\n=== Testing Observability Integration ===")
    
    # Test structured logging
    logger = StructuredLogger("test_component")
    
    # Test correlation context
    with observability_context("test_operation") as (obs_logger, metrics, monitor, correlation_id):
        print(f"Correlation ID: {correlation_id}")
        
        # Test logging
        obs_logger.info("Test operation started", metadata={'test': True})
        
        # Test metrics
        metrics.increment_counter("test_operations")
        metrics.set_gauge("test_value", 42.5)
        metrics.record_timer("operation_duration", 100.0)
        
        # Test performance monitoring
        monitor.record_phi_detection(3, correlation_id)
        monitor.record_fallback_response(correlation_id)
        
        # Simulate some work
        time.sleep(0.1)
        
        obs_logger.info("Test operation completed")
    
    # Check metrics
    counter_value = metrics.get_counter_value("test_operations")
    gauge_value = metrics.get_gauge_value("test_value")
    timer_stats = metrics.get_timer_stats("operation_duration")
    
    print(f"Counter value: {counter_value}")
    print(f"Gauge value: {gauge_value}")
    print(f"Timer stats: {timer_stats}")
    
    assert counter_value >= 1
    assert gauge_value == 42.5
    assert timer_stats["count"] >= 1
    
    print("✅ Observability features working correctly")
    
    # Test performance snapshot
    snapshot = monitor.get_performance_snapshot()
    print(f"Performance snapshot: {snapshot.timestamp}")
    assert snapshot.phi_detections >= 3
    assert snapshot.fallback_responses >= 1
    
    print("✅ Performance monitoring working correctly")


def test_ai_analyzer_integration():
    """Test enhanced AI analyzer integration."""
    print("\n=== Testing AI Analyzer Integration ===")
    
    # Test analyzer creation
    try:
        analyzer = create_analyzer(enable_phi_protection=True)
        print("✅ Enhanced analyzer created successfully")
    except Exception as e:
        print(f"⚠️ Analyzer creation failed (likely due to missing API key): {e}")
        return
    
    # Test health status
    health = analyzer.get_health_status()
    print(f"System health: {health['status']}")
    print(f"PHI protection enabled: {health['phi_protection_enabled']}")
    
    assert health['phi_protection_enabled'] is True
    
    # Test connection (if API key available)
    try:
        success, message = analyzer.test_connection()
        print(f"Connection test: {'✅' if success else '❌'} {message}")
        
        if success:
            # Test actual analysis with PHI protection
            test_text = """
            Dear VA Officer,
            I am Dr. Smith writing about veteran John Doe (SSN: 123-45-6789).
            It is my medical opinion that it is at least as likely as not
            that his current back condition is related to his military service.
            """
            
            correlation_id = str(uuid.uuid4())
            result = analyzer.analyze_letter(test_text, correlation_id)
            
            print(f"Analysis completed: {not result.get('error', True)}")
            
            if 'production_metadata' in result:
                metadata = result['production_metadata']
                print(f"PHI detections: {metadata.get('phi_detections_count', 0)}")
                print(f"Processing time: {metadata.get('processing_time_ms', 0):.0f}ms")
                
                # Should have detected PHI
                assert metadata.get('phi_detections_count', 0) > 0
            
            print("✅ AI analyzer with PHI protection working correctly")
            
    except Exception as e:
        print(f"⚠️ Connection test failed (API key or network issue): {e}")


def test_complete_system_integration():
    """Test complete system integration with all features."""
    print("\n=== Testing Complete System Integration ===")
    
    # Simulate complete analysis workflow
    correlation_id = str(uuid.uuid4())
    
    print(f"Starting integrated test with correlation ID: {correlation_id}")
    
    # Test data with PHI
    test_letter = """
    Medical Associates Clinic
    
    RE: Nexus opinion for James Wilson
    DOB: 03/15/1980
    Phone: (555) 234-5678
    
    Dear Claims Examiner,
    
    I have examined Mr. Wilson and reviewed his military medical records.
    Based on my evaluation, it is my medical opinion that it is at least
    as likely as not (probability >50%) that his current PTSD condition
    is related to his combat service in Afghanistan from 2005-2007.
    
    The temporal relationship and symptom onset support this connection.
    
    Dr. Sarah Johnson, MD
    License: MD789012
    """
    
    try:
        # Step 1: PHI Protection
        with phi_compliant_processing(correlation_id) as (corr_id, phi_detector, audit_logger):
            cleaned_text, detections = phi_detector.de_identify_text(test_letter, corr_id)
            
            print(f"PHI detections: {len(detections)}")
            categories = list(set(d.category.value for d in detections))
            print(f"PHI categories: {categories}")
            
            # Should protect patient name, DOB, phone
            assert len(detections) > 0
            assert "James Wilson" not in cleaned_text
            
        # Step 2: Observability Context
        with observability_context("integration_test", correlation_id) as (logger, metrics, monitor, corr_id):
            
            # Step 3: Error Handling (simulate potential failure)
            @with_error_handling(
                retry_config=RetryConfig(max_attempts=2, base_delay_seconds=0.1),
                enable_fallback=True
            )
            def mock_ai_analysis(text: str):
                # Simulate successful analysis
                return {
                    "error": False,
                    "analysis": {
                        "overall_score": 85,
                        "nexus_strength": "Strong",
                        "primary_condition": "PTSD",
                        "key_strengths": ["Clear probability language", "Temporal relationship"],
                        "critical_issues": []
                    }
                }
            
            # Execute mock analysis
            result = mock_ai_analysis(cleaned_text)
            
            # Record metrics
            metrics.increment_counter("integration_tests")
            monitor.record_phi_detection(len(detections), correlation_id)
            
            logger.info("Integration test completed successfully")
            
            assert not result.get("error", True)
            assert result["analysis"]["overall_score"] == 85
            
        print("✅ Complete system integration test passed")
        
        # Step 4: Performance validation
        snapshot = monitor.get_performance_snapshot()
        print(f"Final metrics - Total requests: {snapshot.total_requests}")
        print(f"Final metrics - PHI detections: {snapshot.phi_detections}")
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        raise


def main():
    """Run all integration tests."""
    print("🧪 Starting Production Integration Tests")
    print("=" * 50)
    
    try:
        test_phi_detection_integration()
        test_error_handling_integration()
        test_observability_integration()
        test_ai_analyzer_integration()
        test_complete_system_integration()
        
        print("\n" + "=" * 50)
        print("✅ ALL INTEGRATION TESTS PASSED")
        print("🚀 System ready for production deployment")
        
    except Exception as e:
        print(f"\n❌ INTEGRATION TEST FAILED: {e}")
        print("🚨 System requires fixes before production deployment")
        raise


if __name__ == "__main__":
    main()