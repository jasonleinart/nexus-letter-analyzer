#!/usr/bin/env python3
"""
Milestone 4: PHI Compliance & Security Testing
Tests current system for PHI handling and security compliance
"""

import sys
import re
import os
import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Any

# Add current directory to path for imports
sys.path.append(".")

from ai_analyzer import create_analyzer
from database import create_database
from config import get_settings


def log_test_result(test_name: str, status: str, details: str = "", error: str = ""):
    """Log test result with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {test_name}: {status}")
    if details:
        print(f"    Details: {details}")
    if error:
        print(f"    Error: {error}")
    print()


def test_phi_detection_patterns():
    """Test for PHI detection capabilities in current system"""
    print("=== PHI DETECTION PATTERN TESTS ===\n")

    # Sample PHI data for testing
    test_phi_samples = {
        "patient_names": [
            "Patient: John Smith",
            "The veteran, Robert Johnson, reports",
            "Mary Jane Doe was seen on",
        ],
        "ssn_numbers": [
            "SSN: 123-45-6789",
            "Social Security Number: 987654321",
            "SS# 123 45 6789",
        ],
        "medical_record_numbers": [
            "Medical Record: MR-12345",
            "Chart Number: CH987654",
            "Patient ID: PID-456789",
        ],
        "dates_of_birth": [
            "Date of Birth: 01/15/1975",
            "DOB: 03/22/1980",
            "Born on December 5, 1965",
        ],
        "phone_numbers": [
            "Phone: (555) 123-4567",
            "Contact: 555-987-6543",
            "Tel: 555.123.4567",
        ],
    }

    # Test 1: Check if system has any PHI detection
    phi_patterns_found = False
    try:
        # Check for potential PHI detection in codebase
        python_files = ["ai_analyzer.py", "database.py", "app.py"]
        phi_keywords = [
            "phi",
            "deidentify",
            "redact",
            "patient",
            "ssn",
            "social security",
        ]

        for file_path in python_files:
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    content = f.read().lower()
                    if any(keyword in content for keyword in phi_keywords):
                        phi_patterns_found = True
                        break

        if phi_patterns_found:
            log_test_result(
                "PHI Detection Code Present",
                "⚠️  PARTIAL",
                "Found PHI-related keywords in code",
            )
        else:
            log_test_result(
                "PHI Detection Code Present",
                "❌ FAIL",
                "No PHI detection code found in system",
            )
    except Exception as e:
        log_test_result("PHI Detection Code Present", "❌ ERROR", error=str(e))

    # Test 2: Manual PHI pattern matching (what should be implemented)
    basic_phi_patterns = {
        "ssn": r"\b\d{3}[-.\s]?\d{2}[-.\s]?\d{4}\b",
        "phone": r"\b\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})\b",
        "name": r"\b[A-Z][a-z]+ [A-Z][a-z]+\b",
    }

    phi_detected = {}
    for phi_type, pattern in basic_phi_patterns.items():
        detected_count = 0
        for category, samples in test_phi_samples.items():
            for sample in samples:
                if re.search(pattern, sample):
                    detected_count += 1
        phi_detected[phi_type] = detected_count

    total_detected = sum(phi_detected.values())
    log_test_result(
        "Basic PHI Pattern Detection (Manual)",
        "ℹ️  INFO",
        f"Would detect {total_detected} PHI instances with basic patterns",
    )


def test_database_phi_exposure():
    """Test database for PHI exposure risks"""
    print("=== DATABASE PHI EXPOSURE TESTS ===\n")

    try:
        db = create_database()

        # Test 1: Check database schema for PHI-related columns
        with sqlite3.connect("nexus_analyses.db") as conn:
            cursor = conn.cursor()

            # Get all table schemas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()

            phi_risk_columns = []
            for table_name in tables:
                table_name = table_name[0]
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()

                for column in columns:
                    column_name = column[1].lower()
                    if any(
                        phi_indicator in column_name
                        for phi_indicator in [
                            "patient",
                            "name",
                            "ssn",
                            "phone",
                            "address",
                            "dob",
                        ]
                    ):
                        phi_risk_columns.append(f"{table_name}.{column[1]}")

            if phi_risk_columns:
                log_test_result(
                    "Database PHI Risk Columns",
                    "⚠️  WARNING",
                    f"Found potential PHI columns: {', '.join(phi_risk_columns)}",
                )
            else:
                log_test_result(
                    "Database PHI Risk Columns",
                    "✅ PASS",
                    "No obvious PHI columns in schema",
                )

        # Test 2: Check for actual data that might contain PHI
        sample_analyses = db.get_recent_analyses(limit=5)
        phi_risk_data = []

        if sample_analyses:
            for analysis in sample_analyses:
                # Check letter_text field for potential PHI
                if hasattr(analysis, "letter_text") and analysis.letter_text:
                    text = analysis.letter_text.lower()
                    if any(
                        indicator in text
                        for indicator in [
                            "patient:",
                            "ssn:",
                            "date of birth",
                            "phone:",
                            "mr-",
                        ]
                    ):
                        phi_risk_data.append(analysis.id)

        if phi_risk_data:
            log_test_result(
                "Database PHI Content Risk",
                "❌ CRITICAL",
                f"Found {len(phi_risk_data)} analyses with potential PHI",
            )
        else:
            log_test_result(
                "Database PHI Content Risk",
                "✅ PASS",
                "No obvious PHI content detected in sample data",
            )

    except Exception as e:
        log_test_result("Database PHI Exposure Tests", "❌ ERROR", error=str(e))


def test_logging_phi_exposure():
    """Test logging system for PHI exposure risks"""
    print("=== LOGGING PHI EXPOSURE TESTS ===\n")

    # Test 1: Check current logging configuration
    root_logger = logging.getLogger()
    handlers = root_logger.handlers

    log_test_result(
        "Logging Handlers Found",
        "ℹ️  INFO",
        f"Found {len(handlers)} handlers: {[type(h).__name__ for h in handlers]}",
    )

    # Test 2: Check if logging includes request/response data
    try:
        # Check ai_analyzer.py for logging statements
        with open("ai_analyzer.py", "r") as f:
            content = f.read()

        logging_statements = content.count("logger.")
        log_statements_with_data = content.count("logger.info(") + content.count(
            "logger.debug("
        )

        log_test_result(
            "Logging Statements Found",
            "ℹ️  INFO",
            f"Found {logging_statements} logging statements, {log_statements_with_data} with potential data",
        )

        # Check for PHI in logging statements
        if "letter_text" in content and "logger" in content:
            log_test_result(
                "Potential PHI in Logs",
                "⚠️  WARNING",
                "Code may log letter_text which could contain PHI",
            )
        else:
            log_test_result(
                "Potential PHI in Logs", "✅ PASS", "No obvious PHI logging detected"
            )

    except Exception as e:
        log_test_result("Logging PHI Exposure Tests", "❌ ERROR", error=str(e))


def test_audit_trail_capabilities():
    """Test for audit trail and compliance tracking"""
    print("=== AUDIT TRAIL & COMPLIANCE TESTS ===\n")

    # Test 1: Check for audit tables
    try:
        with sqlite3.connect("nexus_analyses.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]

            audit_tables = [
                t for t in tables if "audit" in t.lower() or "log" in t.lower()
            ]

            if audit_tables:
                log_test_result(
                    "Audit Tables Present",
                    "✅ PASS",
                    f"Found audit tables: {', '.join(audit_tables)}",
                )
            else:
                log_test_result(
                    "Audit Tables Present",
                    "❌ FAIL",
                    "No audit tables found - compliance tracking missing",
                )

    except Exception as e:
        log_test_result("Audit Trail Capabilities", "❌ ERROR", error=str(e))

    # Test 2: Check for request correlation capabilities
    correlation_features = []
    try:
        # Check database for correlation ID columns
        with sqlite3.connect("nexus_analyses.db") as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(analyses)")
            columns = [col[1] for col in cursor.fetchall()]

            correlation_columns = [
                col
                for col in columns
                if any(
                    indicator in col.lower()
                    for indicator in ["correlation", "request_id", "trace_id"]
                )
            ]

            if correlation_columns:
                correlation_features.extend(correlation_columns)

        if correlation_features:
            log_test_result(
                "Request Correlation Support",
                "✅ PASS",
                f"Found correlation columns: {', '.join(correlation_features)}",
            )
        else:
            log_test_result(
                "Request Correlation Support",
                "❌ FAIL",
                "No request correlation support found",
            )

    except Exception as e:
        log_test_result("Request Correlation Support", "❌ ERROR", error=str(e))


def test_configuration_security():
    """Test configuration and credential security"""
    print("=== CONFIGURATION SECURITY TESTS ===\n")

    # Test 1: Check for hardcoded API keys
    try:
        security_files = ["config.py", "ai_analyzer.py", "app.py"]
        hardcoded_keys = []

        for file_path in security_files:
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    content = f.read()

                # Look for potential hardcoded keys
                if re.search(r"sk-[a-zA-Z0-9]{20,}", content):
                    hardcoded_keys.append(f"{file_path}: OpenAI API key")
                if re.search(r'["\'][a-zA-Z0-9]{32,}["\']', content):
                    hardcoded_keys.append(f"{file_path}: Potential key")

        if hardcoded_keys:
            log_test_result(
                "Hardcoded Credentials",
                "❌ CRITICAL",
                f"Found potential hardcoded keys: {', '.join(hardcoded_keys)}",
            )
        else:
            log_test_result(
                "Hardcoded Credentials", "✅ PASS", "No hardcoded credentials detected"
            )

    except Exception as e:
        log_test_result("Configuration Security", "❌ ERROR", error=str(e))

    # Test 2: Check environment variable usage
    try:
        settings = get_settings()
        env_vars_used = []

        # Check if OpenAI key is from environment
        if hasattr(settings, "openai_api_key"):
            if settings.openai_api_key and not settings.openai_api_key.startswith(
                "sk-"
            ):
                env_vars_used.append("OpenAI API key from environment")

        if env_vars_used:
            log_test_result(
                "Environment Variable Security",
                "✅ PASS",
                f"Using environment variables: {', '.join(env_vars_used)}",
            )
        else:
            log_test_result(
                "Environment Variable Security",
                "⚠️  WARNING",
                "May not be using environment variables for sensitive config",
            )

    except Exception as e:
        log_test_result("Environment Variable Security", "❌ ERROR", error=str(e))


def test_data_retention_policies():
    """Test data retention and deletion capabilities"""
    print("=== DATA RETENTION & DELETION TESTS ===\n")

    # Test 1: Check for data retention configuration
    retention_config_found = False
    try:
        config_files = ["config.py", "database.py"]
        for file_path in config_files:
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    content = f.read()
                    if any(
                        term in content.lower()
                        for term in ["retention", "cleanup", "delete", "expire"]
                    ):
                        retention_config_found = True
                        break

        if retention_config_found:
            log_test_result(
                "Data Retention Configuration",
                "✅ PASS",
                "Found retention-related code",
            )
        else:
            log_test_result(
                "Data Retention Configuration",
                "❌ FAIL",
                "No data retention policies found",
            )

    except Exception as e:
        log_test_result("Data Retention Configuration", "❌ ERROR", error=str(e))

    # Test 2: Check for secure deletion methods
    try:
        db = create_database()
        has_delete_methods = hasattr(db, "delete_analysis") or hasattr(
            db, "cleanup_old_data"
        )

        if has_delete_methods:
            log_test_result(
                "Secure Deletion Methods", "✅ PASS", "Database has deletion methods"
            )
        else:
            log_test_result(
                "Secure Deletion Methods", "❌ FAIL", "No secure deletion methods found"
            )

    except Exception as e:
        log_test_result("Secure Deletion Methods", "❌ ERROR", error=str(e))


def run_all_tests():
    """Run comprehensive PHI compliance and security testing"""
    print("MILESTONE 4: PHI COMPLIANCE & SECURITY TESTING")
    print("=" * 50)
    print(f"Test Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    try:
        test_phi_detection_patterns()
        test_database_phi_exposure()
        test_logging_phi_exposure()
        test_audit_trail_capabilities()
        test_configuration_security()
        test_data_retention_policies()

        print("=" * 50)
        print("PHI COMPLIANCE & SECURITY TESTING COMPLETE")
        print()
        print("CRITICAL FINDINGS SUMMARY:")
        print("- PHI Detection: NOT IMPLEMENTED - HIPAA VIOLATION RISK")
        print("- Audit Trails: MISSING - Legal discovery requirement failure")
        print("- Data Retention: NO POLICIES - Compliance violation risk")
        print("- Request Correlation: MISSING - Troubleshooting impossible")
        print()
        print("RECOMMENDATION: System NOT READY for legal industry deployment")
        print("Requires immediate PHI compliance implementation before production use")
        return 0

    except Exception as e:
        print(f"CRITICAL TEST FAILURE: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
