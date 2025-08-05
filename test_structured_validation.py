#!/usr/bin/env python3
"""
Milestone 4: Structured Validation Testing
Tests existing Pydantic model validation capabilities
"""

import sys
import json
import traceback
from typing import Dict, Any
from datetime import datetime

# Add current directory to path for imports
sys.path.append('.')

from ai_analyzer import NexusAnalysis, ComponentScore


def log_test_result(test_name: str, status: str, details: str = "", error: str = ""):
    """Log test result with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {test_name}: {status}")
    if details:
        print(f"    Details: {details}")
    if error:
        print(f"    Error: {error}")
    print()


def test_component_score_validation():
    """Test ComponentScore Pydantic model validation"""
    print("=== COMPONENT SCORE VALIDATION TESTS ===\n")
    
    # Test 1: Valid ComponentScore creation
    try:
        valid_score = ComponentScore(
            score=22,
            confidence=85,
            findings=["Clear medical opinion present", "Probability language used"],
            issues=["Missing specific probability percentage"],
            rationale="Strong medical evidence with good VA compliance"
        )
        log_test_result("Valid ComponentScore Creation", "✅ PASS", 
                       f"Score: {valid_score.score}, Confidence: {valid_score.confidence}")
    except Exception as e:
        log_test_result("Valid ComponentScore Creation", "❌ FAIL", error=str(e))
    
    # Test 2: Invalid score range (above 25)
    try:
        invalid_score = ComponentScore(
            score=30,  # Invalid - above 25
            confidence=85,
            findings=["Test finding"],
            issues=["Test issue"],
            rationale="Test rationale"
        )
        log_test_result("Invalid Score Range (>25)", "❌ FAIL", 
                       "Should have rejected score > 25")
    except Exception as e:
        log_test_result("Invalid Score Range (>25)", "✅ PASS", 
                       "Correctly rejected invalid score", str(e))
    
    # Test 3: Invalid confidence range (above 100)
    try:
        invalid_confidence = ComponentScore(
            score=20,
            confidence=150,  # Invalid - above 100
            findings=["Test finding"],
            issues=["Test issue"], 
            rationale="Test rationale"
        )
        log_test_result("Invalid Confidence Range (>100)", "❌ FAIL",
                       "Should have rejected confidence > 100")
    except Exception as e:
        log_test_result("Invalid Confidence Range (>100)", "✅ PASS",
                       "Correctly rejected invalid confidence", str(e))
    
    # Test 4: Missing required fields
    try:
        missing_fields = ComponentScore(
            score=20,
            confidence=85
            # Missing findings, issues, rationale
        )
        log_test_result("Missing Required Fields", "❌ FAIL",
                       "Should have rejected missing required fields")
    except Exception as e:
        log_test_result("Missing Required Fields", "✅ PASS",
                       "Correctly rejected missing fields", str(e))


def test_nexus_analysis_validation():
    """Test NexusAnalysis Pydantic model validation"""
    print("=== NEXUS ANALYSIS VALIDATION TESTS ===\n")
    
    # Create valid component scores for testing
    valid_component = ComponentScore(
        score=20,
        confidence=85,
        findings=["Medical opinion present"],
        issues=["Minor formatting issue"],
        rationale="Good medical evidence"
    )
    
    # Test 1: Valid NexusAnalysis creation
    try:
        valid_analysis = NexusAnalysis(
            medical_opinion=valid_component,
            service_connection=valid_component,
            medical_rationale=valid_component,
            professional_format=valid_component,
            overall_score=80,
            nexus_strength="Strong",
            primary_condition="PTSD",
            service_connected_condition="Combat exposure",
            connection_theory="direct",
            probability_language="highly probable",
            summary="Strong nexus letter with clear medical opinion",
            key_strengths=["Clear probability language", "Strong medical rationale", "Proper format"],
            critical_issues=["None identified"],
            improvement_priorities=["Minor formatting improvements"]
        )
        log_test_result("Valid NexusAnalysis Creation", "✅ PASS",
                       f"Overall Score: {valid_analysis.overall_score}, Strength: {valid_analysis.nexus_strength}")
    except Exception as e:
        log_test_result("Valid NexusAnalysis Creation", "❌ FAIL", error=str(e))
    
    # Test 2: Invalid overall score range
    try:
        invalid_score = NexusAnalysis(
            medical_opinion=valid_component,
            service_connection=valid_component,
            medical_rationale=valid_component,
            professional_format=valid_component,
            overall_score=150,  # Invalid - above 100
            nexus_strength="Strong",
            primary_condition="PTSD",
            service_connected_condition="Combat exposure",
            connection_theory="direct",
            summary="Test summary",
            key_strengths=["Test strength"],
            critical_issues=["Test issue"],
            improvement_priorities=["Test improvement"]
        )
        log_test_result("Invalid Overall Score (>100)", "❌ FAIL",
                       "Should have rejected overall score > 100")
    except Exception as e:
        log_test_result("Invalid Overall Score (>100)", "✅ PASS",
                       "Correctly rejected invalid overall score", str(e))
    
    # Test 3: Missing required fields
    try:
        missing_analysis = NexusAnalysis(
            medical_opinion=valid_component,
            service_connection=valid_component,
            medical_rationale=valid_component,
            professional_format=valid_component,
            overall_score=80,
            nexus_strength="Strong"
            # Missing many required fields
        )
        log_test_result("Missing Required Analysis Fields", "❌ FAIL",
                       "Should have rejected missing required fields")
    except Exception as e:
        log_test_result("Missing Required Analysis Fields", "✅ PASS",
                       "Correctly rejected missing fields", str(e))


def test_json_serialization():
    """Test JSON serialization/deserialization of models"""
    print("=== JSON SERIALIZATION TESTS ===\n")
    
    # Create valid models
    try:
        component = ComponentScore(
            score=22,
            confidence=88,
            findings=["Strong medical opinion", "Clear probability language"],
            issues=["Minor formatting"],
            rationale="Excellent medical evidence with proper VA compliance"
        )
        
        analysis = NexusAnalysis(
            medical_opinion=component,
            service_connection=component,
            medical_rationale=component,
            professional_format=component,
            overall_score=88,
            nexus_strength="Strong", 
            primary_condition="PTSD",
            service_connected_condition="Combat stress",
            connection_theory="direct",
            probability_language="highly probable",
            summary="Excellent nexus letter with strong medical foundation",
            key_strengths=["Clear medical opinion", "Strong rationale", "Proper format"],
            critical_issues=["None"],
            improvement_priorities=["Minor formatting polish"]
        )
        
        # Test serialization
        json_data = analysis.model_dump()
        log_test_result("JSON Serialization", "✅ PASS",
                       f"Serialized {len(json_data)} fields")
        
        # Test deserialization
        recreated_analysis = NexusAnalysis(**json_data)
        log_test_result("JSON Deserialization", "✅ PASS",
                       f"Score: {recreated_analysis.overall_score}")
        
        # Verify data integrity
        if recreated_analysis.overall_score == analysis.overall_score:
            log_test_result("Data Integrity Check", "✅ PASS",
                           "Original and recreated models match")
        else:
            log_test_result("Data Integrity Check", "❌ FAIL",
                           "Data corruption detected")
            
    except Exception as e:
        log_test_result("JSON Serialization Tests", "❌ FAIL", error=str(e))


def test_malformed_data_handling():
    """Test handling of malformed or incomplete data"""
    print("=== MALFORMED DATA HANDLING TESTS ===\n")
    
    # Test 1: Partial JSON data (simulating AI response issues)
    partial_data = {
        "medical_opinion": {
            "score": 15,
            "confidence": 70,
            "findings": ["Some medical evidence"],
            "issues": ["Weak rationale"],
            "rationale": "Limited medical support"
        },
        "overall_score": 60,
        "nexus_strength": "Moderate"
        # Missing many required fields
    }
    
    try:
        partial_analysis = NexusAnalysis(**partial_data)
        log_test_result("Partial Data Handling", "❌ FAIL",
                       "Should have rejected incomplete data")
    except Exception as e:
        log_test_result("Partial Data Handling", "✅ PASS", 
                       "Correctly rejected incomplete data", str(e))
    
    # Test 2: Invalid data types
    invalid_types = {
        "medical_opinion": "not_a_component_score",  # Should be ComponentScore
        "overall_score": "not_a_number",  # Should be int
        "nexus_strength": 123  # Should be string
    }
    
    try:
        invalid_analysis = NexusAnalysis(**invalid_types)
        log_test_result("Invalid Data Types", "❌ FAIL",
                       "Should have rejected invalid data types")
    except Exception as e:
        log_test_result("Invalid Data Types", "✅ PASS",
                       "Correctly rejected invalid types", str(e))


def test_edge_cases():
    """Test edge case scenarios"""
    print("=== EDGE CASE TESTS ===\n")
    
    # Test minimum valid values
    try:
        min_component = ComponentScore(
            score=0,  # Minimum valid score
            confidence=0,  # Minimum valid confidence
            findings=[],  # Empty list (should be allowed)
            issues=[],
            rationale=""  # Empty string (may or may not be allowed)
        )
        log_test_result("Minimum Valid Values", "✅ PASS",
                       "Accepted minimum boundary values")
    except Exception as e:
        log_test_result("Minimum Valid Values", "❌ FAIL/EXPECTED",
                       "Rejected minimum values", str(e))
    
    # Test maximum valid values
    try:
        max_component = ComponentScore(
            score=25,  # Maximum valid score
            confidence=100,  # Maximum valid confidence
            findings=["Finding " + str(i) for i in range(100)],  # Large list
            issues=["Issue " + str(i) for i in range(50)],
            rationale="Very long rationale " * 100  # Very long string
        )
        log_test_result("Maximum Valid Values", "✅ PASS",
                       "Accepted maximum boundary values")
    except Exception as e:
        log_test_result("Maximum Valid Values", "❌ FAIL",
                       "Failed on maximum values", str(e))


def run_all_tests():
    """Run comprehensive validation testing suite"""
    print("MILESTONE 4: STRUCTURED VALIDATION TESTING")
    print("=" * 50)
    print(f"Test Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        test_component_score_validation()
        test_nexus_analysis_validation()
        test_json_serialization()
        test_malformed_data_handling()
        test_edge_cases()
        
        print("=" * 50)
        print("STRUCTURED VALIDATION TESTING COMPLETE")
        print("See results above for detailed pass/fail status")
        
    except Exception as e:
        print(f"CRITICAL TEST FAILURE: {str(e)}")
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()