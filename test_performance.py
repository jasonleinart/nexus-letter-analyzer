#!/usr/bin/env python3
"""Performance tests for Nexus Letter AI Analyzer."""

import sys
import time
sys.path.append('.')

from text_processor import create_processor
from ai_analyzer import create_analyzer
from config import get_settings

def run_performance_tests():
    """Run comprehensive performance tests."""
    
    print('=== TEST 4.1: Performance Tests ===')
    
    processor = create_processor()
    analyzer = create_analyzer()
    
    # Test performance with different text sizes
    short_text = 'Short nexus letter with medical opinion about service connection and veteran disability claim. This letter provides basic medical assessment for claim.'
    medium_text = 'Medical nexus letter ' * 50 + ' regarding veteran disability service connection and medical opinion assessment'
    long_text = 'This is a comprehensive medical nexus letter regarding veteran disability service connection. ' * 100 + 'Medical opinion provided by qualified physician regarding service-connected condition.'
    
    performance_tests = [
        (short_text, 'Short letter'),
        (medium_text, 'Medium letter'),
        (long_text, 'Long letter')
    ]
    
    print('Text Processing Performance:')
    for text, description in performance_tests:
        start_time = time.time()
        
        # Test text processing steps
        cleaned = processor.clean_text(text)
        stats = processor.get_text_stats(cleaned)
        is_valid, message = processor.validate_input(cleaned)
        
        processing_time = time.time() - start_time
        
        print(f'{description}:')
        print(f'  Length: {len(text)} chars')
        print(f'  Processing time: {processing_time:.4f} seconds')
        print(f'  Validation: {"PASS" if is_valid else "FAIL"}\n')
    
    print('=== Application Startup Simulation ===')
    # Simulate app startup time
    startup_start = time.time()
    
    # Import all modules (simulates app startup)
    settings = get_settings()
    
    # Initialize processors
    processor = create_processor() 
    analyzer = create_analyzer()
    
    # Test API connection
    success, message = analyzer.test_connection()
    
    startup_time = time.time() - startup_start
    print(f'Simulated app startup time: {startup_time:.2f} seconds')
    print(f'API connection test: {"PASS" if success else "FAIL"} - {message}')
    
    if startup_time < 10:
        print('Startup performance: PASS - Under 10 second requirement')
    else:
        print('Startup performance: FAIL - Exceeds 10 second requirement')
    
    return startup_time < 10

if __name__ == "__main__":
    run_performance_tests()