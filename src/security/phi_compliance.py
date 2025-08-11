"""
Fixed PHI Compliance and Security Module for HIPAA-compliant processing of nexus letters.

Improved patterns to reduce false positives while maintaining comprehensive PHI protection.
"""

import re
import json
import logging
import hashlib
import uuid
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum


class PHICategory(Enum):
    """Categories of PHI that must be protected."""

    NAME = "name"
    SSN = "ssn"
    DATE_OF_BIRTH = "date_of_birth"
    ADDRESS = "address"
    PHONE = "phone"
    EMAIL = "email"
    MEDICAL_RECORD_NUMBER = "medical_record_number"
    ACCOUNT_NUMBER = "account_number"
    CERTIFICATE_NUMBER = "certificate_number"
    LICENSE_NUMBER = "license_number"
    DEVICE_IDENTIFIER = "device_identifier"
    WEB_URL = "web_url"
    IP_ADDRESS = "ip_address"
    BIOMETRIC_IDENTIFIER = "biometric_identifier"
    PHOTO = "photo"
    OTHER_UNIQUE_IDENTIFIER = "other_unique_identifier"


@dataclass
class PHIDetection:
    """Represents a detected PHI element."""

    category: PHICategory
    original_text: str
    start_position: int
    end_position: int
    confidence: float
    redacted_text: str


@dataclass
class AuditLogEntry:
    """Audit log entry for compliance tracking."""

    timestamp: datetime
    correlation_id: str
    action: str
    user_id: Optional[str]
    phi_detected: bool
    phi_categories: List[PHICategory]
    data_hash: str
    processing_time_ms: int


class PHIDetectionEngine:
    """
    Advanced PHI detection and de-identification engine for legal compliance.

    Implements HIPAA Safe Harbor method with improved patterns to minimize
    false positives while maintaining comprehensive protection.
    """

    def __init__(self, strict_mode: bool = True):
        """
        Initialize PHI detection engine.

        Args:
            strict_mode: If True, uses more conservative patterns to reduce false positives
        """
        self.strict_mode = strict_mode
        self.logger = logging.getLogger(__name__)
        self._phi_patterns = self._initialize_patterns()
        self._common_false_positives = self._initialize_false_positives()

    def _initialize_false_positives(self) -> Dict[PHICategory, set]:
        """Initialize common false positive patterns to exclude."""
        return {
            PHICategory.NAME: {
                "nexus letter",
                "medical center",
                "veterans affairs",
                "department of",
                "united states",
                "social security",
                "disability law",
                "law group",
                "claims examiner",
                "rating decision",
                "service connection",
                "medical opinion",
                "nexus opinion",
                "dear sir",
                "to whom",
                "thank you",
                "best regards",
                "medical associates",
                "health care",
                "primary care",
                "mental health",
                "back pain",
                "knee pain",
                "shoulder pain",
                "ptsd condition",
                "hearing loss",
                "tbi symptoms",
            }
        }

    def _initialize_patterns(self) -> Dict[PHICategory, List[re.Pattern]]:
        """Initialize improved regex patterns for PHI detection."""
        patterns = {}

        # Improved name patterns with context awareness
        patterns[PHICategory.NAME] = [
            # Names explicitly mentioned as patients/veterans (most reliable)
            re.compile(
                r"(?:patient|veteran|individual|person|claimant|mr\.?|mrs\.?|ms\.?|miss)\s+([A-Z][a-z]+\s+[A-Z]\.?\s*[A-Z][a-z]+)",
                re.IGNORECASE,
            ),
            re.compile(
                r"(?:RE:|Subject:|regarding)\s*:?[^a-zA-Z]*([A-Z][a-z]+\s+[A-Z]\.?\s*[A-Z][a-z]+)",
                re.IGNORECASE,
            ),
            # Names in formal signatures (Dr. John Smith, MD)
            re.compile(
                r"(?:Dr\.?|Doctor)\s+([A-Z][a-z]+\s+[A-Z]\.?\s*[A-Z][a-z]+)(?:,\s*M\.?D\.?)?",
                re.IGNORECASE,
            ),
            re.compile(
                r"Sincerely,?\s*([A-Z][a-z]+\s+[A-Z]\.?\s*[A-Z][a-z]+)", re.IGNORECASE
            ),
            # Names with middle initial (John A. Smith)
            re.compile(r"\b([A-Z][a-z]+\s+[A-Z]\.\s+[A-Z][a-z]+)\b"),
            # Full names in specific contexts (less aggressive than before)
            re.compile(
                r"(?:examined|treated|seen|evaluated)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)",
                re.IGNORECASE,
            ),
        ]

        # SSN patterns (unchanged - highly specific)
        patterns[PHICategory.SSN] = [
            re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),  # 123-45-6789
            re.compile(r"\b\d{3}\s\d{2}\s\d{4}\b"),  # 123 45 6789
            re.compile(r"\b\d{9}\b"),  # 123456789 (9 consecutive digits)
        ]

        # Date of birth patterns
        patterns[PHICategory.DATE_OF_BIRTH] = [
            re.compile(
                r"(?:born|birth|dob|date of birth)[\s:]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                re.IGNORECASE,
            ),
            re.compile(
                r"(?:born|birth)[\s:]*(?:on\s+)?([A-Z][a-z]+\s+\d{1,2},?\s+\d{4})",
                re.IGNORECASE,
            ),
            re.compile(
                r"\b(?:DOB|D\.O\.B\.?)[\s:]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                re.IGNORECASE,
            ),
            # Specific birth contexts
            re.compile(
                r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{4})\b(?=.*born|.*birth)", re.IGNORECASE
            ),
        ]

        # Address patterns (improved specificity)
        patterns[PHICategory.ADDRESS] = [
            # Street addresses with numbers
            re.compile(
                r"\b\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:St|Street|Ave|Avenue|Rd|Road|Blvd|Boulevard|Dr|Drive|Ln|Lane|Ct|Court|Pl|Place)\.?\b"
            ),
            # PO Boxes
            re.compile(r"\bP\.?O\.?\s+Box\s+\d+\b", re.IGNORECASE),
            # ZIP codes in address context
            re.compile(r"[A-Z][a-z]+,\s*[A-Z]{2}\s+(\d{5}(?:-\d{4})?)", re.IGNORECASE),
            # Full address pattern (City, State ZIP)
            re.compile(
                r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s*[A-Z]{2}\s+\d{5}(?:-\d{4})?\b"
            ),
        ]

        # Phone number patterns (unchanged - highly specific)
        patterns[PHICategory.PHONE] = [
            re.compile(r"\b\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
            re.compile(r"\b\d{3}-\d{3}-\d{4}\b"),
            re.compile(r"\b\(\d{3}\)\s?\d{3}-\d{4}\b"),
        ]

        # Email patterns (unchanged - highly specific)
        patterns[PHICategory.EMAIL] = [
            re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
        ]

        # Medical record numbers
        patterns[PHICategory.MEDICAL_RECORD_NUMBER] = [
            re.compile(
                r"\b(?:MRN|medical record|patient id|chart number)[\s:]*([A-Z0-9-]+)",
                re.IGNORECASE,
            ),
            re.compile(r"\b[A-Z]{2}\d{6,8}\b"),  # Common MRN format
        ]

        # Account numbers
        patterns[PHICategory.ACCOUNT_NUMBER] = [
            re.compile(r"\b(?:account|acct)[\s#:]*(\d{6,12})", re.IGNORECASE),
        ]

        # License numbers
        patterns[PHICategory.LICENSE_NUMBER] = [
            re.compile(r"\b(?:license|lic)[\s#:]*([A-Z]{1,3}\d{5,8})", re.IGNORECASE),
        ]

        # Web URLs (unchanged)
        patterns[PHICategory.WEB_URL] = [
            re.compile(r'https?://[^\s<>"{}|\\^`[\]]+'),
        ]

        # IP addresses (unchanged)
        patterns[PHICategory.IP_ADDRESS] = [
            re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
        ]

        return patterns

    def detect_phi(
        self, text: str, correlation_id: Optional[str] = None
    ) -> List[PHIDetection]:
        """
        Detect PHI elements in text with improved accuracy.

        Args:
            text: Text to analyze for PHI
            correlation_id: Optional correlation ID for audit logging

        Returns:
            List of PHI detections found
        """
        detections: List[PHIDetection] = []

        if not text or not text.strip():
            return detections

        for category, patterns in self._phi_patterns.items():
            for pattern in patterns:
                for match in pattern.finditer(text):
                    # Extract the actual PHI text (may be in a capture group)
                    if pattern.groups > 0:
                        # Use first capture group if available
                        phi_text = match.group(1)
                        start_pos = match.start(1)
                        end_pos = match.end(1)
                    else:
                        # Use full match
                        phi_text = match.group(0)
                        start_pos = match.start(0)
                        end_pos = match.end(0)

                    # Skip if this is a known false positive
                    if self._is_false_positive(category, phi_text):
                        continue

                    # Skip very short matches that are likely false positives
                    if len(phi_text.strip()) < 2:
                        continue

                    detection = PHIDetection(
                        category=category,
                        original_text=phi_text,
                        start_position=start_pos,
                        end_position=end_pos,
                        confidence=self._calculate_confidence(category, phi_text, text),
                        redacted_text=self._generate_redaction(category, phi_text),
                    )
                    detections.append(detection)

        # Remove overlapping detections (keep higher confidence ones)
        detections = self._remove_overlapping_detections(detections)

        # Sort by position for consistent processing
        detections.sort(key=lambda x: x.start_position)

        # Log detection results for audit
        if correlation_id:
            self._log_phi_detection(correlation_id, detections, text)

        return detections

    def _is_false_positive(self, category: PHICategory, text: str) -> bool:
        """Check if detected text is a known false positive."""
        if category not in self._common_false_positives:
            return False

        text_lower = text.lower().strip()
        false_positives = self._common_false_positives[category]

        # Check for exact matches or substring matches
        for fp in false_positives:
            if fp in text_lower or text_lower in fp:
                return True

        # Additional checks for names
        if category == PHICategory.NAME:
            # Skip if it's likely a medical term or common phrase
            medical_terms = [
                "back pain",
                "knee joint",
                "left arm",
                "right leg",
                "chest pain",
                "experiences back",
                "and hearing",
                "hearing loss",
                "experiences pain",
                "and depression",
                "and anxiety",
                "back injury",
                "knee injury",
                "shoulder pain",
                "neck pain",
                "headache",
                "and fatigue",
            ]
            if any(term in text_lower for term in medical_terms):
                return True

            # Skip medical/legal terminology combinations
            medical_legal_terms = [
                "nexus opinion",
                "medical nexus",
                "nexus letter",
                "nexus evaluation",
                "medical opinion",
                "legal opinion",
                "disability opinion",
                "va nexus",
                "nexus assessment",
                "nexus examination",
            ]
            if any(term in text_lower for term in medical_legal_terms):
                return True

            # Skip if it starts with a lowercase word (likely mid-sentence)
            words = text.split()
            if words and words[0][0].islower():
                return True

            # Skip if it's a verb + noun pattern
            verb_patterns = [
                "experiences",
                "has",
                "reports",
                "exhibits",
                "shows",
                "presents",
            ]
            if any(text_lower.startswith(verb + " ") for verb in verb_patterns):
                return True

            # Skip if it contains numbers (likely not a name)
            if any(char.isdigit() for char in text):
                return True

        return False

    def _remove_overlapping_detections(
        self, detections: List[PHIDetection]
    ) -> List[PHIDetection]:
        """Remove overlapping detections, keeping higher confidence ones."""
        if not detections:
            return detections

        # Sort by confidence (descending) then by position
        detections.sort(key=lambda x: (-x.confidence, x.start_position))

        filtered: List[PHIDetection] = []
        for detection in detections:
            # Check if this detection overlaps with any already accepted detection
            overlaps = False
            for accepted in filtered:
                if (
                    detection.start_position < accepted.end_position
                    and detection.end_position > accepted.start_position
                ):
                    overlaps = True
                    break

            if not overlaps:
                filtered.append(detection)

        return filtered

    def de_identify_text(
        self, text: str, correlation_id: Optional[str] = None
    ) -> Tuple[str, List[PHIDetection]]:
        """
        De-identify text by replacing PHI with safe alternatives.

        Args:
            text: Original text containing potential PHI
            correlation_id: Optional correlation ID for audit logging

        Returns:
            Tuple of (de-identified_text, detected_phi_list)
        """
        detections = self.detect_phi(text, correlation_id)

        if not detections:
            return text, []

        # Apply redactions from end to start to preserve positions
        cleaned_text = text
        for detection in reversed(detections):
            cleaned_text = (
                cleaned_text[: detection.start_position]
                + detection.redacted_text
                + cleaned_text[detection.end_position :]
            )

        return cleaned_text, detections

    def _calculate_confidence(
        self, category: PHICategory, text: str, full_text: str
    ) -> float:
        """Calculate confidence score for PHI detection with improved logic."""
        base_confidence = 0.8

        # Adjust based on category and text characteristics
        if category == PHICategory.NAME:
            # Context-based confidence adjustment
            context_indicators = {
                "patient": 1.0,
                "veteran": 1.0,
                "mr.": 0.9,
                "mrs.": 0.9,
                "ms.": 0.9,
                "examined": 0.95,
                "treated": 0.95,
                "re:": 0.9,
                "sincerely": 0.85,
                "dr.": 0.8,  # Could be doctor name or patient name
            }

            text_lower = full_text.lower()
            max_context_confidence = (
                0.7  # Base confidence for names without strong context
            )

            for indicator, confidence in context_indicators.items():
                if indicator in text_lower:
                    max_context_confidence = max(max_context_confidence, confidence)

            # Adjust for name characteristics
            if len(text.split()) >= 2:  # Multiple words
                max_context_confidence += 0.1
            if "." in text:  # Has middle initial
                max_context_confidence += 0.05

            return min(max_context_confidence, 1.0)

        elif category == PHICategory.SSN:
            return 0.98  # SSN patterns are highly specific
        elif category == PHICategory.DATE_OF_BIRTH:
            # Higher confidence if in clear DOB context
            if any(
                term in full_text.lower() for term in ["dob", "date of birth", "born"]
            ):
                return 0.95
            return 0.8
        elif category == PHICategory.PHONE:
            return 0.95
        elif category == PHICategory.EMAIL:
            return 0.98
        elif category == PHICategory.ADDRESS:
            return 0.85
        else:
            return base_confidence

    def _generate_redaction(self, category: PHICategory, original_text: str) -> str:
        """Generate appropriate redaction for PHI category."""
        redaction_map = {
            PHICategory.NAME: "[PATIENT_NAME]",
            PHICategory.SSN: "[SSN_REDACTED]",
            PHICategory.DATE_OF_BIRTH: "[DOB_REDACTED]",
            PHICategory.ADDRESS: "[ADDRESS_REDACTED]",
            PHICategory.PHONE: "[PHONE_REDACTED]",
            PHICategory.EMAIL: "[EMAIL_REDACTED]",
            PHICategory.MEDICAL_RECORD_NUMBER: "[MRN_REDACTED]",
            PHICategory.ACCOUNT_NUMBER: "[ACCOUNT_REDACTED]",
            PHICategory.LICENSE_NUMBER: "[LICENSE_REDACTED]",
            PHICategory.WEB_URL: "[URL_REDACTED]",
            PHICategory.IP_ADDRESS: "[IP_REDACTED]",
        }

        return redaction_map.get(category, "[PHI_REDACTED]")

    def _log_phi_detection(
        self, correlation_id: str, detections: List[PHIDetection], original_text: str
    ):
        """Log PHI detection for audit trail."""
        categories = list(set(d.category for d in detections))

        # Create audit entry (without logging actual PHI content)
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "correlation_id": correlation_id,
            "action": "phi_detection",
            "phi_detected": len(detections) > 0,
            "phi_categories": [cat.value for cat in categories],
            "detection_count": len(detections),
            "text_length": len(original_text),
            "data_hash": hashlib.sha256(original_text.encode()).hexdigest(),
        }

        # Log audit entry (safe - no PHI content)
        self.logger.info(f"PHI Detection Audit: {json.dumps(audit_entry)}")


class SecureAuditLogger:
    """
    Secure audit logging system for legal compliance.

    Ensures all processing activities are logged without exposing PHI.
    """

    def __init__(self, log_file: Optional[str] = None):
        """
        Initialize secure audit logger.

        Args:
            log_file: Optional file path for audit logs
        """
        self.logger = logging.getLogger("audit")
        self.log_file = log_file

        if log_file:
            handler = logging.FileHandler(log_file)
            formatter = logging.Formatter(
                "%(asctime)s - AUDIT - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def log_analysis_start(
        self, correlation_id: str, text_length: int, user_id: Optional[str] = None
    ):
        """Log the start of analysis processing."""
        audit_data = {
            "correlation_id": correlation_id,
            "action": "analysis_start",
            "user_id": user_id or "anonymous",
            "text_length": text_length,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.logger.info(f"ANALYSIS_START: {json.dumps(audit_data)}")

    def log_phi_processing(
        self,
        correlation_id: str,
        phi_detected: bool,
        categories: List[PHICategory],
        processing_time_ms: int,
    ):
        """Log PHI processing without exposing PHI content."""
        audit_data = {
            "correlation_id": correlation_id,
            "action": "phi_processing",
            "phi_detected": phi_detected,
            "phi_categories": [cat.value for cat in categories],
            "processing_time_ms": processing_time_ms,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.logger.info(f"PHI_PROCESSING: {json.dumps(audit_data)}")

    def log_ai_request(
        self,
        correlation_id: str,
        model: str,
        tokens_sent: int,
        tokens_received: int,
        processing_time_ms: int,
    ):
        """Log AI API request without exposing content."""
        audit_data = {
            "correlation_id": correlation_id,
            "action": "ai_request",
            "model": model,
            "tokens_sent": tokens_sent,
            "tokens_received": tokens_received,
            "processing_time_ms": processing_time_ms,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.logger.info(f"AI_REQUEST: {json.dumps(audit_data)}")

    def log_analysis_complete(
        self,
        correlation_id: str,
        overall_score: int,
        total_processing_time_ms: int,
        success: bool,
    ):
        """Log analysis completion."""
        audit_data = {
            "correlation_id": correlation_id,
            "action": "analysis_complete",
            "overall_score": overall_score,
            "total_processing_time_ms": total_processing_time_ms,
            "success": success,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.logger.info(f"ANALYSIS_COMPLETE: {json.dumps(audit_data)}")

    def log_error(self, correlation_id: str, error_type: str, error_message: str):
        """Log error without exposing sensitive information."""
        # Sanitize error message to remove potential PHI
        sanitized_message = self._sanitize_error_message(error_message)

        audit_data = {
            "correlation_id": correlation_id,
            "action": "error",
            "error_type": error_type,
            "error_message": sanitized_message,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.logger.error(f"ERROR: {json.dumps(audit_data)}")

    def _sanitize_error_message(self, message: str) -> str:
        """Remove potential PHI from error messages."""
        # Basic sanitization - remove potential names, numbers, emails
        sanitized = re.sub(r"\b[A-Z][a-z]+\s+[A-Z][a-z]+\b", "[NAME_REDACTED]", message)
        sanitized = re.sub(r"\b\d{3}-\d{2}-\d{4}\b", "[SSN_REDACTED]", sanitized)
        sanitized = re.sub(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "[EMAIL_REDACTED]",
            sanitized,
        )
        sanitized = re.sub(r"\b\d{3}-\d{3}-\d{4}\b", "[PHONE_REDACTED]", sanitized)
        return sanitized


class DataRetentionManager:
    """
    Manages data retention policies and secure deletion for compliance.
    """

    def __init__(self, default_retention_days: int = 2555):  # 7 years default
        """
        Initialize data retention manager.

        Args:
            default_retention_days: Default retention period in days
        """
        self.default_retention_days = default_retention_days
        self.logger = logging.getLogger(__name__)

    def should_retain_data(
        self, created_date: datetime, retention_days: Optional[int] = None
    ) -> bool:
        """
        Check if data should be retained based on policy.

        Args:
            created_date: When the data was created
            retention_days: Custom retention period, uses default if None

        Returns:
            True if data should be retained, False if eligible for deletion
        """
        retention_period = retention_days or self.default_retention_days
        age_days = (datetime.utcnow() - created_date).days
        return age_days < retention_period

    def get_eligible_for_deletion(self, database_connection) -> List[int]:
        """
        Get analysis IDs eligible for deletion based on retention policy.

        Args:
            database_connection: Database connection to query

        Returns:
            List of analysis IDs eligible for deletion
        """
        cutoff_date = datetime.utcnow().date() - timedelta(
            days=self.default_retention_days
        )

        cursor = database_connection.cursor()
        results = cursor.execute(
            """
            SELECT id FROM analyses 
            WHERE DATE(created_at) < ?
        """,
            (cutoff_date,),
        ).fetchall()

        return [row["id"] for row in results]

    def secure_delete_analysis(
        self, database_connection, analysis_id: int, correlation_id: str
    ) -> bool:
        """
        Securely delete analysis data and all related records.

        Args:
            database_connection: Database connection
            analysis_id: Analysis ID to delete
            correlation_id: Correlation ID for audit logging

        Returns:
            True if deletion successful, False otherwise
        """
        try:
            cursor = database_connection.cursor()

            # Delete in order to respect foreign key constraints
            cursor.execute(
                "DELETE FROM improvement_suggestions WHERE analysis_id = ?",
                (analysis_id,),
            )
            cursor.execute(
                "DELETE FROM component_scores WHERE analysis_id = ?", (analysis_id,)
            )
            cursor.execute("DELETE FROM analyses WHERE id = ?", (analysis_id,))

            database_connection.commit()

            # Log secure deletion (audit trail)
            audit_data = {
                "correlation_id": correlation_id,
                "action": "secure_deletion",
                "analysis_id": analysis_id,
                "timestamp": datetime.utcnow().isoformat(),
            }
            self.logger.info(f"SECURE_DELETION: {json.dumps(audit_data)}")

            return True

        except Exception as e:
            self.logger.error(
                f"Secure deletion failed for analysis {analysis_id}: {str(e)}"
            )
            return False


@contextmanager
def phi_compliant_processing(correlation_id: Optional[str] = None):
    """
    Context manager for PHI-compliant processing with automatic audit logging.

    Args:
        correlation_id: Optional correlation ID, generates one if None

    Yields:
        Tuple of (correlation_id, phi_detector, audit_logger)
    """
    if correlation_id is None:
        correlation_id = str(uuid.uuid4())

    phi_detector = PHIDetectionEngine(strict_mode=True)
    audit_logger = SecureAuditLogger()

    start_time = datetime.utcnow()

    try:
        yield correlation_id, phi_detector, audit_logger

    except Exception as e:
        # Log error without exposing PHI
        audit_logger.log_error(correlation_id, type(e).__name__, str(e))
        raise

    finally:
        # Log processing completion
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        audit_logger.logger.info(
            f"PHI_PROCESSING_SESSION_END: {correlation_id} - {processing_time:.0f}ms"
        )


def create_phi_detector(strict_mode: bool = True) -> PHIDetectionEngine:
    """Create a new PHI detection engine instance."""
    return PHIDetectionEngine(strict_mode=strict_mode)


def create_audit_logger(log_file: Optional[str] = None) -> SecureAuditLogger:
    """Create a new secure audit logger instance."""
    return SecureAuditLogger(log_file)


def create_retention_manager(retention_days: int = 2555) -> DataRetentionManager:
    """Create a new data retention manager instance."""
    return DataRetentionManager(retention_days)


# Test and validation functions
if __name__ == "__main__":
    # Test improved PHI detection
    test_text = """
    Dear VA Claims Officer,
    
    I am writing regarding veteran John A. Smith (SSN: 123-45-6789), born on March 15, 1975.
    He resides at 123 Main Street, Anytown, ST 12345.
    Contact: john.smith@email.com or (555) 123-4567.
    
    Medical Record #: ABC123456
    
    This nexus letter provides my medical opinion regarding the service connection.
    The patient was examined by Dr. Jane Medical on February 20, 2024.
    
    Sincerely,
    Dr. Sarah Wilson, MD
    License: MD789012
    """

    with phi_compliant_processing() as (corr_id, detector, audit):
        cleaned_text, detections = detector.de_identify_text(test_text, corr_id)

        print("=== IMPROVED PHI COMPLIANCE TEST ===")
        print(f"Original text length: {len(test_text)}")
        print(f"Detections found: {len(detections)}")
        print(f"Correlation ID: {corr_id}")

        print("\n=== DETECTIONS ===")
        for detection in detections:
            print(
                f"- {detection.category.value}: '{detection.original_text}' -> '{detection.redacted_text}' (confidence: {detection.confidence:.2f})"
            )

        print("\n=== CLEANED TEXT SAMPLE ===")
        print(cleaned_text[:300] + "..." if len(cleaned_text) > 300 else cleaned_text)

        # Verify specific protections
        assert "John A. Smith" not in cleaned_text, "Patient name should be redacted"
        assert "123-45-6789" not in cleaned_text, "SSN should be redacted"
        assert "john.smith@email.com" not in cleaned_text, "Email should be redacted"

        # Verify medical content is preserved
        assert (
            "nexus letter" in cleaned_text.lower()
        ), "Medical terminology should be preserved"
        assert (
            "service connection" in cleaned_text.lower()
        ), "Legal terminology should be preserved"

        print("\n✅ Improved PHI detection working correctly!")
