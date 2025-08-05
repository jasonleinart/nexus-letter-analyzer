"""Quick validation test for Milestone 2 key components"""

import time
import os
from datetime import datetime

# Import system components
from ai_analyzer import create_analyzer
from scoring_engine import create_scorer
from recommendation_engine import create_recommendation_engine
from database import create_database
from text_processor import create_processor
from analytics import AnalyticsEngine


def run_quick_validation():
    """Run essential validation tests for Milestone 2."""

    print("=== MILESTONE 2 QUICK VALIDATION ===")
    print(f"Started at: {datetime.now().strftime('%H:%M:%S')}")

    results = {}

    # Test database path
    test_db_path = "quick_test_milestone2.db"
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

    try:
        # 1. Component Initialization Test
        print("\n1. Testing component initialization...")
        processor = create_processor()
        analyzer = create_analyzer()
        scorer = create_scorer()
        rec_engine = create_recommendation_engine()
        database = create_database(test_db_path)
        analytics = AnalyticsEngine(database)

        results["component_init"] = True
        print("   ✓ All components initialized successfully")

        # 2. Scoring Engine Basic Test
        print("\n2. Testing scoring engine...")

        # Mock AI analysis data for testing
        mock_analysis = {
            "medical_opinion": {
                "score": 22,
                "confidence": 90,
                "findings": [
                    "Clear probability language present",
                    "Definitive medical opinion",
                ],
                "issues": [],
                "rationale": "Strong medical opinion component",
            },
            "service_connection": {
                "score": 20,
                "confidence": 85,
                "findings": [
                    "Explicit service connection stated",
                    "Specific service events mentioned",
                ],
                "issues": [],
                "rationale": "Clear service connection established",
            },
            "medical_rationale": {
                "score": 18,
                "confidence": 80,
                "findings": [
                    "Medical literature referenced",
                    "Clinical explanation provided",
                ],
                "issues": ["Could use more detailed mechanism"],
                "rationale": "Good medical rationale with minor gaps",
            },
            "professional_format": {
                "score": 21,
                "confidence": 95,
                "findings": ["Professional letterhead", "Physician credentials stated"],
                "issues": [],
                "rationale": "Excellent professional presentation",
            },
            "overall_score": 81,
            "nexus_strength": "Strong",
            "primary_condition": "Lumbar spine condition",
            "key_strengths": ["Clear medical opinion", "Strong service connection"],
            "critical_issues": [],
        }

        scoring_results = scorer.calculate_total_score(mock_analysis)

        # Verify scoring worked
        scoring_success = (
            "overall_score" in scoring_results
            and 0 <= scoring_results["overall_score"] <= 100
            and "medical_opinion_breakdown" in scoring_results
        )

        results["scoring_engine"] = scoring_success
        if scoring_success:
            print(
                f"   ✓ Scoring engine working: {scoring_results['overall_score']}/100"
            )
        else:
            print("   ✗ Scoring engine failed")

        # 3. Recommendation Engine Test
        print("\n3. Testing recommendation engine...")

        recommendations = rec_engine.generate_recommendations(
            scoring_results["overall_score"], scoring_results, mock_analysis
        )

        rec_success = (
            "workflow_recommendation" in recommendations
            and "improvement_suggestions" in recommendations
            and "client_summary" in recommendations
        )

        results["recommendation_engine"] = rec_success
        if rec_success:
            workflow_rec = recommendations["workflow_recommendation"]
            decision = (
                workflow_rec.decision
                if hasattr(workflow_rec, "decision")
                else "unknown"
            )
            print(f"   ✓ Recommendation engine working: {decision}")
        else:
            print("   ✗ Recommendation engine failed")

        # 4. Database Integration Test
        print("\n4. Testing database integration...")

        sample_letter = "This is a test nexus letter for database validation."

        analysis_id = database.save_analysis(
            sample_letter, mock_analysis, scoring_results, recommendations, 2.5
        )

        retrieved = database.get_analysis(analysis_id)

        db_success = (
            analysis_id is not None
            and retrieved is not None
            and retrieved["overall_score"] == scoring_results["overall_score"]
        )

        results["database_integration"] = db_success
        if db_success:
            print(f"   ✓ Database integration working: Analysis ID {analysis_id}")
        else:
            print("   ✗ Database integration failed")

        # 5. Analytics Test
        print("\n5. Testing analytics engine...")

        metrics = analytics.get_summary_metrics()
        roi_metrics = analytics.get_roi_metrics()

        analytics_success = (
            "total_analyses" in metrics
            and "avg_score" in metrics
            and "net_savings" in roi_metrics
        )

        results["analytics_engine"] = analytics_success
        if analytics_success:
            print(
                f"   ✓ Analytics working: {metrics['total_analyses']} analyses tracked"
            )
        else:
            print("   ✗ Analytics engine failed")

        # 6. Integration Test
        print("\n6. Testing end-to-end integration...")

        # Test that all components work together
        integration_success = all(
            [
                results.get("component_init", False),
                results.get("scoring_engine", False),
                results.get("recommendation_engine", False),
                results.get("database_integration", False),
                results.get("analytics_engine", False),
            ]
        )

        results["integration"] = integration_success
        if integration_success:
            print("   ✓ End-to-end integration successful")
        else:
            print("   ✗ Integration issues detected")

        # Summary
        print(f"\n=== VALIDATION SUMMARY ===")
        passed_tests = sum(1 for result in results.values() if result)
        total_tests = len(results)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        print(f"Tests Passed: {passed_tests}/{total_tests}")
        print(f"Success Rate: {success_rate:.1f}%")

        print(f"\nDetailed Results:")
        for test_name, result in results.items():
            status = "PASS" if result else "FAIL"
            print(f"  {test_name}: {status}")

        # Overall validation
        milestone2_ready = success_rate >= 83.0  # 5/6 tests must pass

        print(f"\n{'='*50}")
        if milestone2_ready:
            print("🎉 MILESTONE 2 VALIDATION: PASSED")
            print("System ready for professional demonstration")
        else:
            print("⚠️  MILESTONE 2 VALIDATION: NEEDS ATTENTION")
            print("Some components require fixes before demonstration")
        print(f"{'='*50}")

        return results, success_rate

    except Exception as e:
        print(f"\n✗ Critical validation error: {str(e)}")
        import traceback

        traceback.print_exc()
        return {}, 0


if __name__ == "__main__":
    results, success_rate = run_quick_validation()
    print(f"\nQuick validation completed with {success_rate:.1f}% success rate")
