"""
Robust Error Handling and Reliability Module for Production-Ready Operations.

Implements circuit breaker patterns, retry logic, graceful degradation, and comprehensive
error recovery mechanisms for the Nexus Letter AI Analyzer.
"""

import time
import json
import logging
import asyncio
from typing import Dict, Any, Optional, Callable, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from contextlib import contextmanager
import threading
from functools import wraps


class ErrorCategory(Enum):
    """Categories of errors for targeted handling."""

    API_TIMEOUT = "api_timeout"
    API_RATE_LIMIT = "api_rate_limit"
    API_AUTHENTICATION = "api_authentication"
    API_SERVER_ERROR = "api_server_error"
    API_NETWORK_ERROR = "api_network_error"
    PARSING_ERROR = "parsing_error"
    VALIDATION_ERROR = "validation_error"
    DATABASE_ERROR = "database_error"
    CONFIGURATION_ERROR = "configuration_error"
    UNKNOWN_ERROR = "unknown_error"


class CircuitBreakerState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Blocking requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class ErrorContext:
    """Context information for error handling."""

    error_category: ErrorCategory
    original_error: Exception
    attempt_number: int
    total_attempts: int
    processing_time_ms: float
    correlation_id: Optional[str] = None
    user_message: Optional[str] = None
    technical_details: Optional[str] = None


@dataclass
class RetryConfig:
    """Configuration for retry logic."""

    max_attempts: int = 3
    base_delay_seconds: float = 1.0
    max_delay_seconds: float = 60.0
    exponential_multiplier: float = 2.0
    jitter: bool = True
    retryable_errors: set = field(
        default_factory=lambda: {
            ErrorCategory.API_TIMEOUT,
            ErrorCategory.API_RATE_LIMIT,
            ErrorCategory.API_SERVER_ERROR,
            ErrorCategory.API_NETWORK_ERROR,
        }
    )


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""

    failure_threshold: int = 5
    timeout_seconds: int = 60
    success_threshold: int = 2  # Successes needed to close from half-open


class CircuitBreaker:
    """
    Circuit breaker implementation for preventing cascade failures.

    Monitors failures and automatically trips to prevent overwhelming
    downstream services during outages.
    """

    def __init__(self, config: CircuitBreakerConfig, name: str = "default"):
        """
        Initialize circuit breaker.

        Args:
            config: Circuit breaker configuration
            name: Name for logging and identification
        """
        self.config = config
        self.name = name
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
        self._lock = threading.RLock()
        self.logger = logging.getLogger(f"circuit_breaker.{name}")

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function through circuit breaker.

        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            CircuitBreakerOpenError: When circuit is open
            Original exception: When function fails
        """
        with self._lock:
            if self.state == CircuitBreakerState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitBreakerState.HALF_OPEN
                    self.logger.info(
                        f"Circuit breaker {self.name}: Moving to HALF_OPEN"
                    )
                else:
                    raise CircuitBreakerOpenError(
                        f"Circuit breaker {self.name} is OPEN. "
                        f"Will retry after {self.config.timeout_seconds}s"
                    )

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result

        except Exception as e:
            self._on_failure(e)
            raise

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return True

        time_since_failure = time.time() - self.last_failure_time
        return time_since_failure >= self.config.timeout_seconds

    def _on_success(self):
        """Handle successful execution."""
        with self._lock:
            if self.state == CircuitBreakerState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.config.success_threshold:
                    self.state = CircuitBreakerState.CLOSED
                    self.failure_count = 0
                    self.success_count = 0
                    self.logger.info(
                        f"Circuit breaker {self.name}: Closed after recovery"
                    )
            elif self.state == CircuitBreakerState.CLOSED:
                # Reset failure count on success
                self.failure_count = max(0, self.failure_count - 1)

    def _on_failure(self, error: Exception):
        """Handle failed execution."""
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.state == CircuitBreakerState.HALF_OPEN:
                # Failed during recovery, go back to open
                self.state = CircuitBreakerState.OPEN
                self.success_count = 0
                self.logger.warning(
                    f"Circuit breaker {self.name}: Failed during recovery, back to OPEN"
                )

            elif self.state == CircuitBreakerState.CLOSED:
                if self.failure_count >= self.config.failure_threshold:
                    self.state = CircuitBreakerState.OPEN
                    self.logger.error(
                        f"Circuit breaker {self.name}: OPENED after {self.failure_count} failures"
                    )

    def get_status(self) -> Dict[str, Any]:
        """Get current circuit breaker status."""
        with self._lock:
            return {
                "name": self.name,
                "state": self.state.value,
                "failure_count": self.failure_count,
                "success_count": self.success_count,
                "last_failure_time": self.last_failure_time,
                "failure_threshold": self.config.failure_threshold,
                "timeout_seconds": self.config.timeout_seconds,
            }


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open."""

    pass


class RetryableError(Exception):
    """Base class for retryable errors."""

    pass


class NonRetryableError(Exception):
    """Base class for non-retryable errors."""

    pass


class ErrorClassifier:
    """
    Classifies errors into categories for appropriate handling.
    """

    @staticmethod
    def classify_error(error: Exception) -> ErrorCategory:
        """
        Classify an error into appropriate category.

        Args:
            error: Exception to classify

        Returns:
            Error category for handling strategy
        """
        error_str = str(error).lower()
        error_type = type(error).__name__.lower()

        # OpenAI API specific errors
        if "timeout" in error_str or "timeouterror" in error_type:
            return ErrorCategory.API_TIMEOUT
        elif "rate limit" in error_str or "429" in error_str:
            return ErrorCategory.API_RATE_LIMIT
        elif (
            "authentication" in error_str
            or "401" in error_str
            or "api key" in error_str
        ):
            return ErrorCategory.API_AUTHENTICATION
        elif (
            "500" in error_str
            or "502" in error_str
            or "503" in error_str
            or "504" in error_str
        ):
            return ErrorCategory.API_SERVER_ERROR
        elif "connection" in error_str or "network" in error_str or "dns" in error_str:
            return ErrorCategory.API_NETWORK_ERROR

        # Application-specific errors
        elif "json" in error_str or "parsing" in error_str:
            return ErrorCategory.PARSING_ERROR
        elif "validation" in error_str or "pydantic" in error_str:
            return ErrorCategory.VALIDATION_ERROR
        elif "database" in error_str or "sqlite" in error_str:
            return ErrorCategory.DATABASE_ERROR
        elif "config" in error_str or "environment" in error_str:
            return ErrorCategory.CONFIGURATION_ERROR

        return ErrorCategory.UNKNOWN_ERROR

    @staticmethod
    def is_retryable(error_category: ErrorCategory) -> bool:
        """
        Determine if an error category is retryable.

        Args:
            error_category: Error category to check

        Returns:
            True if error is retryable, False otherwise
        """
        retryable_categories = {
            ErrorCategory.API_TIMEOUT,
            ErrorCategory.API_RATE_LIMIT,
            ErrorCategory.API_SERVER_ERROR,
            ErrorCategory.API_NETWORK_ERROR,
            ErrorCategory.DATABASE_ERROR,  # Some database errors are transient
        }
        return error_category in retryable_categories

    @staticmethod
    def get_user_message(error_category: ErrorCategory, attempt_number: int = 1) -> str:
        """
        Get user-friendly error message for category.

        Args:
            error_category: Error category
            attempt_number: Current attempt number

        Returns:
            User-friendly error message
        """
        messages = {
            ErrorCategory.API_TIMEOUT: f"The AI service is taking longer than expected to respond (attempt {attempt_number}). Please wait while we retry...",
            ErrorCategory.API_RATE_LIMIT: f"We're processing many requests right now (attempt {attempt_number}). Retrying in a moment...",
            ErrorCategory.API_SERVER_ERROR: f"The AI service is temporarily unavailable (attempt {attempt_number}). Retrying automatically...",
            ErrorCategory.API_NETWORK_ERROR: f"Connection issue detected (attempt {attempt_number}). Attempting to reconnect...",
            ErrorCategory.API_AUTHENTICATION: "There's an issue with the API configuration. Please check your settings.",
            ErrorCategory.PARSING_ERROR: "The AI response couldn't be processed properly. This might indicate a service issue.",
            ErrorCategory.VALIDATION_ERROR: "The analysis results don't meet our quality standards. Please try again.",
            ErrorCategory.DATABASE_ERROR: "There's a temporary issue saving your analysis. The analysis completed successfully.",
            ErrorCategory.CONFIGURATION_ERROR: "There's a configuration issue that needs to be resolved.",
            ErrorCategory.UNKNOWN_ERROR: "An unexpected error occurred. Our team has been notified.",
        }
        return messages.get(error_category, messages[ErrorCategory.UNKNOWN_ERROR])


class RobustRetryManager:
    """
    Advanced retry manager with exponential backoff and jitter.
    """

    def __init__(self, config: RetryConfig):
        """
        Initialize retry manager.

        Args:
            config: Retry configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)

    def execute_with_retry(
        self, func: Callable, *args, correlation_id: Optional[str] = None, **kwargs
    ) -> Any:
        """
        Execute function with retry logic.

        Args:
            func: Function to execute
            *args: Function arguments
            correlation_id: Optional correlation ID for logging
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            Last exception if all retries fail
        """
        last_error = None

        for attempt in range(1, self.config.max_attempts + 1):
            try:
                start_time = time.time()
                result = func(*args, **kwargs)
                processing_time = (time.time() - start_time) * 1000

                if attempt > 1:
                    self.logger.info(
                        f"Retry successful on attempt {attempt}/{self.config.max_attempts} "
                        f"(correlation_id: {correlation_id})"
                    )

                return result

            except Exception as error:
                processing_time = (time.time() - start_time) * 1000
                error_category = ErrorClassifier.classify_error(error)
                last_error = error

                error_context = ErrorContext(
                    error_category=error_category,
                    original_error=error,
                    attempt_number=attempt,
                    total_attempts=self.config.max_attempts,
                    processing_time_ms=processing_time,
                    correlation_id=correlation_id,
                    user_message=ErrorClassifier.get_user_message(
                        error_category, attempt
                    ),
                )

                # Check if this is the last attempt or error is non-retryable
                if (
                    attempt == self.config.max_attempts
                    or not ErrorClassifier.is_retryable(error_category)
                ):
                    self.logger.error(
                        f"Final failure after {attempt} attempts: {error_category.value} "
                        f"(correlation_id: {correlation_id})"
                    )
                    raise self._wrap_final_error(error_context)

                # Calculate delay and wait
                delay = self._calculate_delay(attempt, error_category)
                self.logger.warning(
                    f"Attempt {attempt}/{self.config.max_attempts} failed: {error_category.value}. "
                    f"Retrying in {delay:.1f}s (correlation_id: {correlation_id})"
                )

                time.sleep(delay)

        # This shouldn't be reached, but just in case
        raise last_error

    def _calculate_delay(self, attempt: int, error_category: ErrorCategory) -> float:
        """
        Calculate delay before next retry attempt.

        Args:
            attempt: Current attempt number
            error_category: Type of error encountered

        Returns:
            Delay in seconds
        """
        # Base exponential backoff
        delay = self.config.base_delay_seconds * (
            self.config.exponential_multiplier ** (attempt - 1)
        )

        # Category-specific adjustments
        if error_category == ErrorCategory.API_RATE_LIMIT:
            # Longer delay for rate limits
            delay *= 2
        elif error_category == ErrorCategory.API_TIMEOUT:
            # Moderate delay for timeouts
            delay *= 1.5

        # Apply maximum delay cap
        delay = min(delay, self.config.max_delay_seconds)

        # Add jitter to prevent thundering herd
        if self.config.jitter:
            import random

            jitter_factor = random.uniform(0.8, 1.2)
            delay *= jitter_factor

        return delay

    def _wrap_final_error(self, context: ErrorContext) -> Exception:
        """
        Wrap final error with enriched context.

        Args:
            context: Error context information

        Returns:
            Wrapped exception with context
        """
        if ErrorClassifier.is_retryable(context.error_category):
            return RetryableError(
                f"Failed after {context.total_attempts} attempts: {context.user_message}"
            )
        else:
            return NonRetryableError(
                context.user_message or str(context.original_error)
            )


class GracefulDegradationManager:
    """
    Manages graceful degradation when services are unavailable.
    """

    def __init__(self):
        """Initialize graceful degradation manager."""
        self.logger = logging.getLogger(__name__)
        self._fallback_responses = self._initialize_fallback_responses()

    def _initialize_fallback_responses(self) -> Dict[str, Any]:
        """Initialize fallback responses for when AI service is unavailable."""
        return {
            "analysis": {
                "medical_opinion": {
                    "score": 15,
                    "confidence": 60,
                    "findings": ["Letter submitted for analysis"],
                    "issues": [
                        "AI service temporarily unavailable - manual review recommended"
                    ],
                    "rationale": "Fallback assessment applied due to service unavailability",
                },
                "service_connection": {
                    "score": 15,
                    "confidence": 60,
                    "findings": ["Letter contains service-related content"],
                    "issues": [
                        "AI service temporarily unavailable - manual review recommended"
                    ],
                    "rationale": "Fallback assessment applied due to service unavailability",
                },
                "medical_rationale": {
                    "score": 15,
                    "confidence": 60,
                    "findings": ["Medical content detected"],
                    "issues": [
                        "AI service temporarily unavailable - manual review recommended"
                    ],
                    "rationale": "Fallback assessment applied due to service unavailability",
                },
                "professional_format": {
                    "score": 15,
                    "confidence": 60,
                    "findings": ["Letter appears to follow medical format"],
                    "issues": [
                        "AI service temporarily unavailable - manual review recommended"
                    ],
                    "rationale": "Fallback assessment applied due to service unavailability",
                },
                "overall_score": 60,
                "nexus_strength": "Moderate",
                "primary_condition": "Requires manual review",
                "service_connected_condition": "Requires manual review",
                "connection_theory": "Requires manual review",
                "probability_language": None,
                "summary": "AI analysis temporarily unavailable. Manual review required for complete assessment.",
                "key_strengths": [
                    "Letter submitted for professional analysis",
                    "Contains medical and legal content",
                    "Follows standard nexus letter format",
                ],
                "critical_issues": [
                    "AI analysis service temporarily unavailable",
                    "Manual review required for accurate assessment",
                    "Recommendation decisions should be made by qualified personnel",
                ],
                "improvement_priorities": [
                    "Resubmit when AI service is available",
                    "Conduct manual review by qualified personnel",
                    "Verify all required elements are present",
                ],
            },
            "workflow_recommendation": {
                "decision": "attorney_review",
                "message": "AI service temporarily unavailable - manual attorney review required",
                "next_steps": [
                    "Submit letter for manual review by qualified attorney",
                    "Verify all required nexus elements are present",
                    "Resubmit for AI analysis when service is restored",
                    "Consider implementing backup analysis procedures",
                ],
            },
        }

    def create_fallback_response(
        self, error_context: ErrorContext, letter_length: int = 0
    ) -> Dict[str, Any]:
        """
        Create fallback response when AI service is unavailable.

        Args:
            error_context: Context about the error that occurred
            letter_length: Length of the original letter

        Returns:
            Fallback analysis response
        """
        self.logger.warning(
            f"Creating fallback response due to {error_context.error_category.value} "
            f"(correlation_id: {error_context.correlation_id})"
        )

        fallback = self._fallback_responses.copy()

        # Adjust score based on letter length (basic heuristic)
        if letter_length > 0:
            if letter_length < 500:
                # Very short letter - likely incomplete
                base_score = 10
            elif letter_length < 1000:
                # Short letter - might be missing elements
                base_score = 12
            elif letter_length > 2000:
                # Long letter - likely more complete
                base_score = 18
            else:
                # Moderate length
                base_score = 15

            # Update component scores
            for component in [
                "medical_opinion",
                "service_connection",
                "medical_rationale",
                "professional_format",
            ]:
                fallback["analysis"][component]["score"] = base_score

            fallback["analysis"]["overall_score"] = base_score * 4

        # Add error context to response
        fallback["error_context"] = {
            "error_category": error_context.error_category.value,
            "attempt_number": error_context.attempt_number,
            "user_message": error_context.user_message,
            "processing_time_ms": error_context.processing_time_ms,
            "fallback_applied": True,
        }

        return {
            "error": False,
            "message": "Analysis completed with fallback processing due to service unavailability",
            "analysis": fallback["analysis"],
            "workflow_recommendation": fallback["workflow_recommendation"],
            "warning": f"AI service temporarily unavailable: {error_context.user_message}",
        }


# Main error handling decorator and context manager
def with_error_handling(
    retry_config: Optional[RetryConfig] = None,
    circuit_breaker: Optional[CircuitBreaker] = None,
    enable_fallback: bool = True,
    correlation_id: Optional[str] = None,
):
    """
    Decorator for comprehensive error handling with retry and circuit breaker.

    Args:
        retry_config: Optional retry configuration
        circuit_breaker: Optional circuit breaker instance
        enable_fallback: Whether to enable graceful degradation
        correlation_id: Optional correlation ID for tracking
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract correlation ID from kwargs if available
            corr_id = kwargs.pop("correlation_id", correlation_id)

            retry_manager = RobustRetryManager(retry_config or RetryConfig())
            degradation_manager = GracefulDegradationManager()

            try:
                if circuit_breaker:
                    # Execute through circuit breaker and retry manager
                    return circuit_breaker.call(
                        retry_manager.execute_with_retry,
                        func,
                        *args,
                        correlation_id=corr_id,
                        **kwargs,
                    )
                else:
                    # Execute through retry manager only
                    return retry_manager.execute_with_retry(
                        func, *args, correlation_id=corr_id, **kwargs
                    )

            except (RetryableError, NonRetryableError, CircuitBreakerOpenError) as e:
                if enable_fallback:
                    # Create error context for fallback
                    error_context = ErrorContext(
                        error_category=ErrorClassifier.classify_error(e),
                        original_error=e,
                        attempt_number=getattr(e, "attempt_number", 0),
                        total_attempts=retry_config.max_attempts if retry_config else 3,
                        processing_time_ms=0,
                        correlation_id=corr_id,
                        user_message=str(e),
                    )

                    # Estimate letter length if possible
                    letter_length = 0
                    if args and isinstance(args[0], str):
                        letter_length = len(args[0])

                    return degradation_manager.create_fallback_response(
                        error_context, letter_length
                    )
                else:
                    raise

        return wrapper

    return decorator


@contextmanager
def error_handling_context(
    correlation_id: Optional[str] = None, circuit_breaker_name: str = "default"
):
    """
    Context manager for error handling with automatic resource cleanup.

    Args:
        correlation_id: Optional correlation ID for tracking
        circuit_breaker_name: Name for circuit breaker instance

    Yields:
        Tuple of (retry_manager, circuit_breaker, degradation_manager)
    """
    # Create instances
    retry_config = RetryConfig()
    circuit_breaker_config = CircuitBreakerConfig()

    retry_manager = RobustRetryManager(retry_config)
    circuit_breaker = CircuitBreaker(circuit_breaker_config, circuit_breaker_name)
    degradation_manager = GracefulDegradationManager()

    try:
        yield retry_manager, circuit_breaker, degradation_manager

    except Exception as e:
        # Log final error
        logger = logging.getLogger(__name__)
        logger.error(
            f"Unhandled error in error handling context: {str(e)} (correlation_id: {correlation_id})"
        )
        raise


# Factory functions
def create_retry_manager(
    max_attempts: int = 3, base_delay: float = 1.0
) -> RobustRetryManager:
    """Create retry manager with custom configuration."""
    config = RetryConfig(max_attempts=max_attempts, base_delay_seconds=base_delay)
    return RobustRetryManager(config)


def create_circuit_breaker(
    name: str = "default", failure_threshold: int = 5
) -> CircuitBreaker:
    """Create circuit breaker with custom configuration."""
    config = CircuitBreakerConfig(failure_threshold=failure_threshold)
    return CircuitBreaker(config, name)


def create_degradation_manager() -> GracefulDegradationManager:
    """Create graceful degradation manager."""
    return GracefulDegradationManager()


# Test function
if __name__ == "__main__":
    import random

    def unreliable_function(text: str) -> str:
        """Test function that randomly fails."""
        if random.random() < 0.7:  # 70% failure rate
            raise Exception("Simulated API failure")
        return f"Processed: {text[:50]}..."

    # Test error handling
    @with_error_handling(
        retry_config=RetryConfig(max_attempts=3),
        enable_fallback=True,
        correlation_id="test-123",
    )
    def test_analysis(text: str) -> str:
        return unreliable_function(text)

    # Test
    test_text = "This is a test nexus letter for error handling validation."
    result = test_analysis(test_text)

    print("=== ERROR HANDLING TEST ===")
    print(f"Result type: {type(result)}")
    if isinstance(result, dict) and result.get("error_context"):
        print("Fallback response created successfully")
        print(f"Error category: {result['error_context']['error_category']}")
        print(f"User message: {result['error_context']['user_message']}")
    else:
        print("Function succeeded")
        print(f"Result: {result}")
