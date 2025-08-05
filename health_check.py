#!/usr/bin/env python3
"""
Simple health check script for Docker container health monitoring.
Returns 0 for healthy, 1 for unhealthy.
"""

import sys
import requests
import time
from typing import Dict, Any

def check_streamlit_health(url: str = "http://localhost:8501", timeout: int = 5) -> bool:
    """
    Check if Streamlit application is responding.
    
    Args:
        url: Base URL of the Streamlit application
        timeout: Request timeout in seconds
        
    Returns:
        True if healthy, False otherwise
    """
    try:
        # Try to access the main page
        response = requests.get(url, timeout=timeout)
        
        # Streamlit should return 200 OK
        if response.status_code == 200:
            return True
            
        print(f"Streamlit returned status code: {response.status_code}")
        return False
        
    except requests.exceptions.ConnectionError:
        print("Connection refused - Streamlit may not be running")
        return False
    except requests.exceptions.Timeout:
        print(f"Request timed out after {timeout} seconds")
        return False
    except Exception as e:
        print(f"Health check failed: {str(e)}")
        return False

def check_system_health() -> Dict[str, Any]:
    """
    Perform comprehensive system health check.
    
    Returns:
        Dictionary with health status information
    """
    health_status = {
        'timestamp': time.time(),
        'status': 'healthy',
        'checks': {}
    }
    
    # Check Streamlit application
    streamlit_healthy = check_streamlit_health()
    health_status['checks']['streamlit'] = {
        'status': 'healthy' if streamlit_healthy else 'unhealthy',
        'message': 'Streamlit is responding' if streamlit_healthy else 'Streamlit is not responding'
    }
    
    # Check if any critical services are down
    critical_failures = [
        check for check, status in health_status['checks'].items() 
        if status['status'] == 'unhealthy'
    ]
    
    if critical_failures:
        health_status['status'] = 'unhealthy'
        health_status['failures'] = critical_failures
    
    return health_status

def main():
    """Main health check entry point."""
    try:
        health = check_system_health()
        
        if health['status'] == 'healthy':
            print("Health check passed - all systems operational")
            sys.exit(0)
        else:
            print(f"Health check failed - status: {health['status']}")
            print(f"Failed checks: {health.get('failures', [])}")
            sys.exit(1)
            
    except Exception as e:
        print(f"Health check error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()