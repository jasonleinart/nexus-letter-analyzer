#!/usr/bin/env python3
"""
Comprehensive Error Handling and Circuit Breaker Testing for Milestone 4.

Tests the robust error handling system, circuit breaker patterns, retry logic,
and graceful degradation capabilities.
"""

import sys
import time
import json
import uuid
import threading
from datetime import datetime
from typing import Dict, Any, List
from unittest.mock import Mock, patch

# Import production modules
from error_handling import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerOpenError,
    RobustRetryManager,
    RetryConfig,
    ErrorClassifier,
    ErrorCategory,
    GracefulDegradationManager,
    with_error_handling,
    error_handling_context,
)


class ErrorHandlingTestSuite:
    """Comprehensive test suite for error handling and reliability features."""

    def __init__(self):
        self.test_results = []
        self.correlation_id = str(uuid.uuid4())

    def log_test_result(self, test_name: str, status: str, details: Dict[str, Any]):
        """Log test result with timestamp and correlation ID."""
        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "correlation_id": self.correlation_id,
            "test_name": test_name,
            "status": status,
            "details": details,
        }
        self.test_results.append(result)

        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_emoji} {test_name}: {status}")

        if details.get("notes"):
            print(f"   Notes: {details['notes']}")
        if details.get("execution_time"):
            print(f"   Time: {details['execution_time']:.0f}ms")

    def test_circuit_breaker_functionality(self):
        """Test circuit breaker opening, closing, and half-open states."""
        config = CircuitBreakerConfig(
            failure_threshold=3,
            timeout_seconds=1,  # Short timeout for testing
            success_threshold=2,
        )
        breaker = CircuitBreaker(config, "test_breaker")

        def failing_function():
            raise Exception("Simulated API failure")

        def succeeding_function():
            return "Success"

        # Test initial closed state
        status = breaker.get_status()
        initial_closed = status["state"] == "closed"

        # Test circuit breaker opening after failures
        failures = 0
        for i in range(5):  # More than threshold
            try:
                breaker.call(failing_function)
            except Exception:
                failures += 1

        status_after_failures = breaker.get_status()
        opened_after_failures = status_after_failures["state"] == "open"

        # Test circuit breaker blocking calls when open
        call_blocked = False
        try:
            breaker.call(failing_function)
        except CircuitBreakerOpenError:
            call_blocked = True

        # Wait for timeout period
        time.sleep(1.1)

        # Test half-open state and recovery
        recovery_attempts = 0
        recovered = False

        for i in range(3):  # Try to recover
            try:
                result = breaker.call(succeeding_function)
                recovery_attempts += 1
                if result == "Success":
                    recovered = True
            except CircuitBreakerOpenError:
                pass  # Still in timeout
            except Exception:
                pass  # Function failed

        final_status = breaker.get_status()

        success = (
            initial_closed
            and opened_after_failures
            and call_blocked
            and failures >= config.failure_threshold
            and recovery_attempts > 0
        )

        self.log_test_result(
            "Circuit Breaker Functionality",
            "PASS" if success else "FAIL",
            {
                "initial_state": "closed" if initial_closed else "not_closed",
                "opened_after_failures": opened_after_failures,
                "failures_recorded": failures,
                "call_blocked_when_open": call_blocked,
                "recovery_attempts": recovery_attempts,
                "final_state": final_status["state"],
                "notes": f"Circuit breaker completed full open/close cycle with {failures} failures",
            },
        )

    def test_retry_logic_with_exponential_backoff(self):
        """Test retry logic with exponential backoff and jitter."""
        config = RetryConfig(
            max_attempts=3,
            base_delay_seconds=0.1,  # Short delays for testing
            exponential_multiplier=2.0,
            jitter=True,
        )
        retry_manager = RobustRetryManager(config)

        # Test function that fails first 2 times, succeeds on 3rd
        call_count = 0

        def intermittently_failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                # Use a retryable error message
                raise Exception("Request timeout after 5 seconds")
            return f"Success on attempt {call_count}"

        start_time = time.time()

        try:
            result = retry_manager.execute_with_retry(
                intermittently_failing_function, correlation_id=self.correlation_id
            )
            execution_time = (time.time() - start_time) * 1000
            success = True
            final_result = result
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            success = False
            final_result = str(e)

        # Test exponential backoff timing (should have delays)
        expected_min_time = (
            (config.base_delay_seconds + config.base_delay_seconds * 2) * 1000 * 0.8
        )  # Account for jitter
        backoff_timing_correct = execution_time >= expected_min_time

        self.log_test_result(
            "Retry Logic with Exponential Backoff",
            (
                "PASS"
                if success and call_count == 3 and backoff_timing_correct
                else "FAIL"
            ),
            {
                "attempts_made": call_count,
                "execution_time": execution_time,
                "expected_min_time": expected_min_time,
                "backoff_timing_correct": backoff_timing_correct,
                "final_result": final_result,
                "success": success,
                "notes": f"Function succeeded after {call_count} attempts in {execution_time:.0f}ms",
            },
        )

    def test_error_classification_accuracy(self):
        """Test error classification for different types of errors."""
        test_errors = [
            (Exception("Request timeout after 30 seconds"), ErrorCategory.API_TIMEOUT),
            (Exception("Rate limit exceeded (429)"), ErrorCategory.API_RATE_LIMIT),
            (
                Exception("Invalid API key authentication failed"),
                ErrorCategory.API_AUTHENTICATION,
            ),
            (Exception("Server error 500 internal"), ErrorCategory.API_SERVER_ERROR),
            (
                Exception("Connection refused network error"),
                ErrorCategory.API_NETWORK_ERROR,
            ),
            (
                Exception("JSON parsing failed invalid format"),
                ErrorCategory.PARSING_ERROR,
            ),
            (Exception("Pydantic validation error"), ErrorCategory.VALIDATION_ERROR),
            (
                Exception("Database connection failed sqlite"),
                ErrorCategory.DATABASE_ERROR,
            ),
            (
                Exception("Configuration missing environment variable"),
                ErrorCategory.CONFIGURATION_ERROR,
            ),
            (Exception("Completely unknown error type"), ErrorCategory.UNKNOWN_ERROR),
        ]

        classification_results = []
        correct_classifications = 0

        for error, expected_category in test_errors:
            classified_category = ErrorClassifier.classify_error(error)
            is_correct = classified_category == expected_category

            if is_correct:
                correct_classifications += 1

            classification_results.append(
                {
                    "error_message": str(error),
                    "expected_category": expected_category.value,
                    "classified_category": classified_category.value,
                    "correct": is_correct,
                }
            )

        accuracy = (correct_classifications / len(test_errors)) * 100
        success = accuracy >= 90  # 90% accuracy requirement

        self.log_test_result(
            "Error Classification Accuracy",
            "PASS" if success else "FAIL",
            {
                "total_tests": len(test_errors),
                "correct_classifications": correct_classifications,
                "accuracy_percentage": accuracy,
                "classification_results": classification_results,
                "notes": f"Error classification accuracy: {accuracy:.1f}% (target: ≥90%)",
            },
        )

    def test_graceful_degradation_fallback(self):
        """Test graceful degradation with fallback responses."""
        degradation_manager = GracefulDegradationManager()

        # Simulate different error contexts
        from error_handling import ErrorContext

        test_contexts = [
            ErrorContext(
                error_category=ErrorCategory.API_TIMEOUT,
                original_error=Exception("Timeout"),
                attempt_number=3,
                total_attempts=3,
                processing_time_ms=30000,
                correlation_id=self.correlation_id,
                user_message="API timeout occurred",
            ),
            ErrorContext(
                error_category=ErrorCategory.API_RATE_LIMIT,
                original_error=Exception("Rate limit"),
                attempt_number=2,
                total_attempts=3,
                processing_time_ms=5000,
                correlation_id=self.correlation_id,
                user_message="Rate limit exceeded",
            ),
        ]

        fallback_results = []

        for context in test_contexts:
            fallback_response = degradation_manager.create_fallback_response(
                context, 1500
            )

            # Validate fallback response structure
            has_required_fields = all(
                key in fallback_response
                for key in ["error", "message", "analysis", "workflow_recommendation"]
            )

            has_analysis_structure = "analysis" in fallback_response and isinstance(
                fallback_response["analysis"], dict
            )

            has_error_context = "error_context" in fallback_response.get("analysis", {})

            fallback_results.append(
                {
                    "error_category": context.error_category.value,
                    "has_required_fields": has_required_fields,
                    "has_analysis_structure": has_analysis_structure,
                    "has_error_context": has_error_context,
                    "response_valid": has_required_fields and has_analysis_structure,
                }
            )

        valid_responses = sum(1 for r in fallback_results if r["response_valid"])
        success = valid_responses == len(test_contexts)

        self.log_test_result(
            "Graceful Degradation Fallback",
            "PASS" if success else "FAIL",
            {
                "contexts_tested": len(test_contexts),
                "valid_responses": valid_responses,
                "fallback_results": fallback_results,
                "success_rate": f"{(valid_responses/len(test_contexts))*100:.1f}%",
                "notes": f"Generated {valid_responses}/{len(test_contexts)} valid fallback responses",
            },
        )

    def test_error_handling_decorator(self):
        """Test error handling decorator with retry and circuit breaker integration."""

        # Create test function with decorator
        call_count = 0

        @with_error_handling(
            retry_config=RetryConfig(max_attempts=2, base_delay_seconds=0.1),
            enable_fallback=True,
            correlation_id=self.correlation_id,
        )
        def test_function_with_retries(text: str):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("Request timeout after 5 seconds")
            return {"analysis": {"overall_score": 75}, "success": True}

        # Test decorator functionality
        start_time = time.time()

        try:
            result = test_function_with_retries("test input")
            execution_time = (time.time() - start_time) * 1000
            decorator_success = True

            # Check if result has expected structure
            result_valid = isinstance(result, dict) and (
                "analysis" in result or "error" in result
            )

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            decorator_success = False
            result_valid = False
            result = str(e)

        success = decorator_success and result_valid and call_count == 2

        self.log_test_result(
            "Error Handling Decorator",
            "PASS" if success else "FAIL",
            {
                "attempts_made": call_count,
                "decorator_success": decorator_success,
                "result_valid": result_valid,
                "execution_time": execution_time,
                "result_preview": str(result)[:100],
                "notes": f"Decorator handled retry logic with {call_count} attempts",
            },
        )

    def test_concurrent_circuit_breaker_behavior(self):
        """Test circuit breaker behavior under concurrent load."""
        config = CircuitBreakerConfig(
            failure_threshold=3, timeout_seconds=0.5, success_threshold=2
        )
        breaker = CircuitBreaker(config, "concurrent_test")

        results = []
        threads = []

        def worker_function(worker_id: int):
            """Worker function for concurrent testing."""
            try:
                # Simulate work that fails for some workers
                if worker_id < 4:  # First 4 workers fail
                    result = breaker.call(
                        lambda: (_ for _ in ()).throw(Exception("Worker failure"))
                    )
                else:  # Later workers should be blocked
                    result = breaker.call(lambda: f"Worker {worker_id} success")
                results.append(
                    {"worker_id": worker_id, "result": result, "status": "success"}
                )
            except CircuitBreakerOpenError:
                results.append(
                    {"worker_id": worker_id, "result": "blocked", "status": "blocked"}
                )
            except Exception as e:
                results.append(
                    {"worker_id": worker_id, "result": str(e), "status": "failed"}
                )

        # Start concurrent workers
        for i in range(8):
            thread = threading.Thread(target=worker_function, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Analyze results
        failed_workers = [r for r in results if r["status"] == "failed"]
        blocked_workers = [r for r in results if r["status"] == "blocked"]
        success_workers = [r for r in results if r["status"] == "success"]

        # Circuit breaker should open after threshold failures
        circuit_opened = len(blocked_workers) > 0
        failure_threshold_respected = len(failed_workers) >= config.failure_threshold

        final_status = breaker.get_status()

        success = circuit_opened and failure_threshold_respected

        self.log_test_result(
            "Concurrent Circuit Breaker Behavior",
            "PASS" if success else "FAIL",
            {
                "total_workers": len(results),
                "failed_workers": len(failed_workers),
                "blocked_workers": len(blocked_workers),
                "success_workers": len(success_workers),
                "circuit_opened": circuit_opened,
                "final_breaker_state": final_status["state"],
                "failure_count": final_status["failure_count"],
                "notes": f"Circuit breaker blocked {len(blocked_workers)} workers after {len(failed_workers)} failures",
            },
        )

    def test_end_to_end_error_recovery(self):
        """Test complete error recovery scenario from failure to recovery."""

        # Create circuit breaker and retry manager
        cb_config = CircuitBreakerConfig(failure_threshold=2, timeout_seconds=0.5)
        retry_config = RetryConfig(max_attempts=2, base_delay_seconds=0.1)

        breaker = CircuitBreaker(cb_config, "recovery_test")
        retry_manager = RobustRetryManager(retry_config)

        phase_results = []

        # Phase 1: Cause circuit breaker to open
        def always_failing_function():
            raise Exception("Service unavailable")

        failures = 0
        for i in range(3):  # Exceed failure threshold
            try:
                breaker.call(always_failing_function)
            except:
                failures += 1

        status_after_failures = breaker.get_status()
        phase_results.append(
            {
                "phase": "failure_accumulation",
                "failures": failures,
                "breaker_state": status_after_failures["state"],
                "success": status_after_failures["state"] == "open",
            }
        )

        # Phase 2: Test that circuit breaker blocks calls
        blocked_calls = 0
        for i in range(2):
            try:
                breaker.call(lambda: "should be blocked")
            except CircuitBreakerOpenError:
                blocked_calls += 1
            except:
                pass

        phase_results.append(
            {
                "phase": "blocking_verification",
                "blocked_calls": blocked_calls,
                "success": blocked_calls == 2,
            }
        )

        # Phase 3: Wait for timeout and test recovery
        time.sleep(0.6)  # Wait for timeout

        def recovering_function():
            return "Service recovered"

        recovery_success = False
        try:
            # Should transition to half-open, then success should close it
            result1 = breaker.call(recovering_function)
            result2 = breaker.call(recovering_function)  # Second success to fully close
            recovery_success = (
                result1 == "Service recovered" and result2 == "Service recovered"
            )
        except:
            recovery_success = False

        final_status = breaker.get_status()
        phase_results.append(
            {
                "phase": "recovery",
                "recovery_success": recovery_success,
                "final_state": final_status["state"],
                "success": recovery_success and final_status["state"] == "closed",
            }
        )

        # Overall success: all phases succeeded
        overall_success = all(phase["success"] for phase in phase_results)

        self.log_test_result(
            "End-to-End Error Recovery",
            "PASS" if overall_success else "FAIL",
            {
                "phases_completed": len(phase_results),
                "phases_successful": sum(1 for p in phase_results if p["success"]),
                "phase_results": phase_results,
                "overall_success": overall_success,
                "final_breaker_state": final_status["state"],
                "notes": f"Complete failure → blocking → recovery cycle with {failures} initial failures",
            },
        )

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all error handling tests and return comprehensive results."""
        print("=" * 60)
        print("⚡ COMPREHENSIVE ERROR HANDLING TESTING")
        print("=" * 60)
        print(f"Correlation ID: {self.correlation_id}")
        print(f"Start Time: {datetime.utcnow().isoformat()}")
        print()

        # Execute all test methods
        test_methods = [
            self.test_circuit_breaker_functionality,
            self.test_retry_logic_with_exponential_backoff,
            self.test_error_classification_accuracy,
            self.test_graceful_degradation_fallback,
            self.test_error_handling_decorator,
            self.test_concurrent_circuit_breaker_behavior,
            self.test_end_to_end_error_recovery,
        ]

        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                self.log_test_result(
                    test_method.__name__.replace("test_", "").replace("_", " ").title(),
                    "ERROR",
                    {
                        "error_message": str(e),
                        "error_type": type(e).__name__,
                        "notes": f"Test execution failed: {str(e)}",
                    },
                )
            print()

        # Calculate summary statistics
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["status"] == "PASS")
        failed_tests = sum(1 for r in self.test_results if r["status"] == "FAIL")
        error_tests = sum(1 for r in self.test_results if r["status"] == "ERROR")

        pass_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0

        summary = {
            "timestamp": datetime.utcnow().isoformat(),
            "correlation_id": self.correlation_id,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "error_tests": error_tests,
            "pass_rate": pass_rate,
            "overall_status": "PASS" if pass_rate >= 85 else "FAIL",
            "detailed_results": self.test_results,
        }

        print("=" * 60)
        print("📊 ERROR HANDLING TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Errors: {error_tests} ⚠️")
        print(f"Pass Rate: {pass_rate:.1f}%")
        print(
            f"Overall Status: {'✅ PASS' if summary['overall_status'] == 'PASS' else '❌ FAIL'}"
        )
        print()

        return summary


if __name__ == "__main__":
    # Run comprehensive error handling testing
    test_suite = ErrorHandlingTestSuite()
    results = test_suite.run_all_tests()

    # Save results to log file
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    log_filename = f"milestone_4_error_handling_retest_{timestamp}.log"

    with open(f"test_logs/{log_filename}", "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"📁 Detailed results saved to: test_logs/{log_filename}")

    # Exit with appropriate code for CI/CD
    exit_code = 0 if results["overall_status"] == "PASS" else 1
    sys.exit(exit_code)
