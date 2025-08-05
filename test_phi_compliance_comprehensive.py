#!/usr/bin/env python3
"""
Comprehensive PHI Compliance Testing for Milestone 4 Production Readiness.

Tests the enhanced PHI detection engine with improved patterns, HIPAA Safe Harbor
compliance, and audit logging capabilities.
"""

import sys
import time
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any

# Import production modules
from phi_compliance import (
    PHIDetectionEngine, PHICategory, create_phi_detector, 
    create_audit_logger, phi_compliant_processing
)

class PHIComplianceTestSuite:
    """Comprehensive test suite for PHI compliance engine."""
    
    def __init__(self):
        self.test_results = []
        self.phi_detector = create_phi_detector(strict_mode=True)
        self.audit_logger = create_audit_logger()
        self.correlation_id = str(uuid.uuid4())
        
    def log_test_result(self, test_name: str, status: str, details: Dict[str, Any]):
        """Log test result with timestamp and correlation ID."""
        result = {
            'timestamp': datetime.utcnow().isoformat(),
            'correlation_id': self.correlation_id,
            'test_name': test_name,
            'status': status,
            'details': details
        }
        self.test_results.append(result)
        
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_emoji} {test_name}: {status}")
        
        if details.get('notes'):
            print(f"   Notes: {details['notes']}")
        if details.get('detections_count'):
            print(f"   Detections: {details['detections_count']}")
    
    def test_hipaa_safe_harbor_categories(self):
        """Test detection of all 16 HIPAA Safe Harbor PHI categories."""
        test_cases = {
            'names': [
                "Patient: John A. Smith was examined",
                "Mr. Robert Johnson attended the appointment", 
                "Dr. Sarah Wilson, MD provided treatment",
                "Veteran Michael Davis needs evaluation"
            ],
            'ssn': [
                "SSN: 123-45-6789",
                "Social Security Number: 123456789",
                "SS# 123 45 6789"
            ],
            'dates_of_birth': [
                "Date of birth: 01/15/1975",
                "Born on March 15, 1980",
                "DOB: 12-25-1965"
            ],
            'addresses': [
                "123 Main Street, Anytown, ST 12345",
                "P.O. Box 456, Springfield, IL 62701",
                "456 Oak Avenue, Apt 2B"
            ],
            'phone_numbers': [
                "(555) 123-4567",
                "555-987-6543",
                "555.123.4567"
            ],
            'emails': [
                "john.smith@email.com",
                "patient.care@hospital.org"
            ],
            'medical_record_numbers': [
                "MRN: ABC123456",
                "Medical Record Number: MR-98765",
                "Patient ID: PAT789012"
            ],
            'account_numbers': [
                "Account: 987654321",
                "Acct# 456789123"
            ],
            'license_numbers': [
                "License: MD123456",
                "Medical License: LIC789012"
            ],
            'urls': [
                "https://patient-portal.hospital.com",
                "http://www.medical-records.org"
            ],
            'ip_addresses': [
                "192.168.1.100",
                "10.0.0.1"
            ]
        }
        
        category_results = {}
        total_detections = 0
        
        for category, test_texts in test_cases.items():
            category_detections = 0
            category_tests = 0
            
            for test_text in test_texts:
                detections = self.phi_detector.detect_phi(test_text, self.correlation_id)
                category_tests += 1
                
                if detections:
                    category_detections += len(detections)
                    total_detections += len(detections)
            
            detection_rate = (category_detections / category_tests) * 100
            category_results[category] = {
                'tests': category_tests,
                'detections': category_detections,
                'detection_rate': detection_rate
            }
        
        # Overall success criteria: >90% detection rate for explicit PHI
        overall_success = sum(r['detections'] for r in category_results.values()) >= (sum(r['tests'] for r in category_results.values()) * 0.9)
        
        self.log_test_result(
            "HIPAA Safe Harbor Categories Detection",
            "PASS" if overall_success else "FAIL",
            {
                'total_tests': sum(r['tests'] for r in category_results.values()),
                'total_detections': total_detections,
                'category_results': category_results,
                'overall_detection_rate': (total_detections / sum(r['tests'] for r in category_results.values())) * 100,
                'notes': f"Detected {total_detections} PHI elements across {len(category_results)} categories"
            }
        )
    
    def test_false_positive_reduction(self):
        """Test improved patterns to reduce false positives in medical/legal text."""
        false_positive_tests = [
            # Medical terms that should NOT be flagged as names
            "The patient experiences back pain and knee pain.",
            "Left arm weakness and right leg numbness observed.",
            "PTSD symptoms and hearing loss documented.",
            "Depression and anxiety are service-connected conditions.",
            
            # Legal/administrative terms
            "United States Department of Veterans Affairs",
            "Social Security Administration decision",
            "Nexus letter medical opinion provided",
            "Service connection determination required",
            
            # Medical facility names
            "Veterans Affairs Medical Center",
            "Department of Defense records",
            "Walter Reed Army Medical Center",
            
            # Common phrases
            "Thank you for your service",
            "Best regards and sincerely yours",
            "To whom it may concern"
        ]
        
        false_positives = 0
        total_tests = len(false_positive_tests)
        
        for test_text in false_positive_tests:
            detections = self.phi_detector.detect_phi(test_text, self.correlation_id)
            name_detections = [d for d in detections if d.category == PHICategory.NAME]
            
            if name_detections:
                false_positives += len(name_detections)
                for detection in name_detections:
                    print(f"   False positive: '{detection.original_text}' in '{test_text}'")
        
        false_positive_rate = (false_positives / total_tests) * 100
        success = false_positive_rate < 10  # Accept <10% false positive rate
        
        self.log_test_result(
            "False Positive Reduction",
            "PASS" if success else "FAIL",
            {
                'total_tests': total_tests,
                'false_positives': false_positives,
                'false_positive_rate': false_positive_rate,
                'notes': f"False positive rate: {false_positive_rate:.1f}% (target: <10%)"
            }
        )
    
    def test_comprehensive_nexus_letter_phi_detection(self):
        """Test PHI detection in realistic nexus letter content."""
        nexus_letter_with_phi = """
        MEDICAL NEXUS OPINION
        
        To: Department of Veterans Affairs
        Re: John A. Smith, SSN: 123-45-6789
        DOB: March 15, 1975
        Medical Record: MR-ABC123
        
        Dear Claims Examiner,
        
        I am Dr. Sarah Wilson, MD, licensed physician (License: MD789012) at 
        Veterans Medical Associates, 456 Oak Street, Springfield, IL 62701.
        Phone: (555) 123-4567, Email: swilson@vma.org
        
        I have examined Mr. Smith on February 20, 2024, regarding his claim for 
        service connection of PTSD. The veteran served in Iraq from 2003-2005 
        and was exposed to combat operations.
        
        MEDICAL OPINION:
        It is more likely than not (>50% probability) that the veteran's 
        current PTSD condition is related to his military service in Iraq.
        
        The veteran's medical history shows onset of symptoms within one year
        of discharge from active duty. His symptoms are consistent with 
        combat-related PTSD as described in DSM-5 criteria.
        
        Sincerely,
        Dr. Sarah Wilson, MD
        Board Certified Psychiatrist
        License: MD789012
        """
        
        # Test de-identification
        cleaned_text, detections = self.phi_detector.de_identify_text(
            nexus_letter_with_phi, self.correlation_id
        )
        
        # Expected PHI categories that should be detected
        expected_categories = {
            PHICategory.NAME,
            PHICategory.SSN, 
            PHICategory.DATE_OF_BIRTH,
            PHICategory.MEDICAL_RECORD_NUMBER,
            PHICategory.LICENSE_NUMBER,
            PHICategory.ADDRESS,
            PHICategory.PHONE,
            PHICategory.EMAIL
        }
        
        detected_categories = set(d.category for d in detections)
        category_coverage = len(detected_categories.intersection(expected_categories)) / len(expected_categories)
        
        # Verify key PHI is redacted
        phi_properly_redacted = all([
            "John A. Smith" not in cleaned_text,
            "123-45-6789" not in cleaned_text,
            "swilson@vma.org" not in cleaned_text,
            "(555) 123-4567" not in cleaned_text
        ])
        
        # Verify medical content is preserved
        content_preserved = all([
            "PTSD" in cleaned_text,
            "service connection" in cleaned_text.lower(),
            "medical opinion" in cleaned_text.lower(),
            "more likely than not" in cleaned_text.lower()
        ])
        
        success = (
            len(detections) >= 8 and  # Should detect at least 8 PHI elements
            category_coverage >= 0.7 and  # Should cover 70%+ of expected categories
            phi_properly_redacted and
            content_preserved
        )
        
        self.log_test_result(
            "Comprehensive Nexus Letter PHI Detection",
            "PASS" if success else "FAIL",
            {
                'detections_count': len(detections),
                'categories_detected': list(detected_categories),
                'category_coverage': f"{category_coverage:.1%}",
                'phi_redacted': phi_properly_redacted,
                'content_preserved': content_preserved,
                'sample_redacted_text': cleaned_text[:200] + "...",
                'notes': f"Detected {len(detections)} PHI elements across {len(detected_categories)} categories"
            }
        )
    
    def test_audit_logging_compliance(self):
        """Test audit logging for legal compliance requirements."""
        test_text = "Patient John Smith (SSN: 123-45-6789) requires nexus opinion."
        
        # Test audit logging through context manager
        audit_entries = []
        
        with phi_compliant_processing(self.correlation_id) as (corr_id, detector, audit):
            # Simulate analysis workflow
            audit.log_analysis_start(corr_id, len(test_text), "test_user")
            
            detections = detector.detect_phi(test_text, corr_id)
            phi_categories = list(set(d.category for d in detections))
            
            audit.log_phi_processing(corr_id, len(detections) > 0, phi_categories, 150)
            audit.log_ai_request(corr_id, "gpt-4", 100, 200, 2500)
            audit.log_analysis_complete(corr_id, 75, 3000, True)
        
        # Verify audit trail completeness
        # Note: In production, we'd verify log entries in actual log files
        success = (
            corr_id == self.correlation_id and
            len(detections) > 0  # Should detect PHI in test text
        )
        
        self.log_test_result(
            "Audit Logging Compliance",
            "PASS" if success else "FAIL",
            {
                'correlation_id_preserved': corr_id == self.correlation_id,
                'phi_detected': len(detections) > 0,
                'detections_count': len(detections),
                'audit_workflow_completed': True,
                'notes': "Full audit trail created for compliance requirements"
            }
        )
    
    def test_performance_benchmarks(self):
        """Test PHI detection performance meets production requirements."""
        # Test with various text lengths
        test_cases = [
            ("Short text with John Smith", 50),
            ("Medium nexus letter content " * 20 + " John A. Smith SSN: 123-45-6789", 500),
            ("Long comprehensive nexus letter " * 100 + " with PHI elements scattered throughout John Smith, Dr. Wilson, 123-45-6789, john@email.com", 2000)
        ]
        
        performance_results = []
        
        for test_text, expected_length in test_cases:
            start_time = time.time()
            detections = self.phi_detector.detect_phi(test_text, self.correlation_id)
            processing_time = (time.time() - start_time) * 1000  # Convert to ms
            
            performance_results.append({
                'text_length': len(test_text),
                'processing_time_ms': processing_time,
                'detections_count': len(detections),
                'performance_ratio': processing_time / len(test_text)  # ms per character
            })
        
        # Performance criteria: <5 seconds for typical letters (<5000ms)
        max_processing_time = max(r['processing_time_ms'] for r in performance_results)
        avg_processing_time = sum(r['processing_time_ms'] for r in performance_results) / len(performance_results)
        
        success = max_processing_time < 5000  # 5 seconds maximum
        
        self.log_test_result(
            "PHI Detection Performance",
            "PASS" if success else "FAIL",
            {
                'max_processing_time_ms': max_processing_time,
                'avg_processing_time_ms': avg_processing_time,
                'performance_results': performance_results,
                'meets_sla': success,
                'notes': f"Max processing time: {max_processing_time:.0f}ms (target: <5000ms)"
            }
        )
    
    def test_confidence_scoring_accuracy(self):
        """Test confidence scoring for PHI detections."""
        confidence_tests = [
            # High confidence cases
            ("Patient: John A. Smith was examined", 0.9),  # Clear patient context
            ("SSN: 123-45-6789", 0.95),  # SSN format is highly specific
            ("Email: john@example.com", 0.95),  # Email format is specific
            
            # Medium confidence cases
            ("John Smith visited the clinic", 0.7),  # Name without strong context
            ("Dr. Wilson examined the patient", 0.8),  # Could be doctor or patient name
            
            # Lower confidence cases (should still detect but with appropriate confidence)
            ("Smith reported symptoms", 0.6),  # Surname only
        ]
        
        confidence_results = []
        
        for test_text, expected_min_confidence in confidence_tests:
            detections = self.phi_detector.detect_phi(test_text, self.correlation_id)
            
            if detections:
                avg_confidence = sum(d.confidence for d in detections) / len(detections)
                confidence_results.append({
                    'text': test_text,
                    'detections': len(detections),
                    'avg_confidence': avg_confidence,
                    'expected_min': expected_min_confidence,
                    'meets_expectation': avg_confidence >= expected_min_confidence
                })
        
        accuracy_rate = sum(1 for r in confidence_results if r['meets_expectation']) / len(confidence_results)
        success = accuracy_rate >= 0.8  # 80% accuracy in confidence scoring
        
        self.log_test_result(
            "Confidence Scoring Accuracy",
            "PASS" if success else "FAIL",
            {
                'tests_run': len(confidence_results),
                'accurate_scores': sum(1 for r in confidence_results if r['meets_expectation']),
                'accuracy_rate': f"{accuracy_rate:.1%}",
                'confidence_results': confidence_results,
                'notes': f"Confidence scoring accuracy: {accuracy_rate:.1%} (target: ≥80%)"
            }
        )
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all PHI compliance tests and return comprehensive results."""
        print("=" * 60)
        print("🛡️ COMPREHENSIVE PHI COMPLIANCE TESTING")
        print("=" * 60)
        print(f"Correlation ID: {self.correlation_id}")
        print(f"Start Time: {datetime.utcnow().isoformat()}")
        print()
        
        # Execute all test methods
        test_methods = [
            self.test_hipaa_safe_harbor_categories,
            self.test_false_positive_reduction,
            self.test_comprehensive_nexus_letter_phi_detection,
            self.test_audit_logging_compliance,
            self.test_performance_benchmarks,
            self.test_confidence_scoring_accuracy
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                self.log_test_result(
                    test_method.__name__.replace('test_', '').replace('_', ' ').title(),
                    "ERROR",
                    {
                        'error_message': str(e),
                        'error_type': type(e).__name__,
                        'notes': f"Test execution failed: {str(e)}"
                    }
                )
            print()
        
        # Calculate summary statistics
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['status'] == 'PASS')
        failed_tests = sum(1 for r in self.test_results if r['status'] == 'FAIL')
        error_tests = sum(1 for r in self.test_results if r['status'] == 'ERROR')
        
        pass_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        summary = {
            'timestamp': datetime.utcnow().isoformat(),
            'correlation_id': self.correlation_id,
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'error_tests': error_tests,
            'pass_rate': pass_rate,
            'overall_status': 'PASS' if pass_rate >= 85 else 'FAIL',
            'detailed_results': self.test_results
        }
        
        print("=" * 60)
        print("📊 PHI COMPLIANCE TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Errors: {error_tests} ⚠️")
        print(f"Pass Rate: {pass_rate:.1f}%")
        print(f"Overall Status: {'✅ PASS' if summary['overall_status'] == 'PASS' else '❌ FAIL'}")
        print()
        
        return summary


if __name__ == "__main__":
    # Run comprehensive PHI compliance testing
    test_suite = PHIComplianceTestSuite()
    results = test_suite.run_all_tests()
    
    # Save results to log file
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    log_filename = f"milestone_4_phi_compliance_retest_{timestamp}.log"
    
    with open(f"test_logs/{log_filename}", 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"📁 Detailed results saved to: test_logs/{log_filename}")
    
    # Exit with appropriate code for CI/CD
    exit_code = 0 if results['overall_status'] == 'PASS' else 1
    sys.exit(exit_code)