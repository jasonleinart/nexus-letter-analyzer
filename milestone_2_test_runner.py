"""Comprehensive test runner for Milestone 2 based on test_plan_draft.md"""

import time
import json
import statistics
import os
from typing import Dict, List, Tuple, Any
from datetime import datetime

# Import system components
from ai_analyzer import create_analyzer
from scoring_engine import create_scorer
from recommendation_engine import create_recommendation_engine
from database import create_database
from text_processor import create_processor
from analytics import AnalyticsEngine


class Milestone2TestRunner:
    """Comprehensive test runner for Milestone 2 validation."""

    def __init__(self):
        """Initialize test runner with fresh components."""
        self.test_db_path = "test_milestone2_validation.db"
        self.results = {}
        self.test_log = []
        self.start_time = datetime.now()

        # Remove existing test database
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test result."""
        status = "PASS" if passed else "FAIL"
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {test_name}: {status}"
        if details:
            log_entry += f" - {details}"

        self.test_log.append(log_entry)
        print(log_entry)

        if test_name not in self.results:
            self.results[test_name] = []
        self.results[test_name].append(passed)

    def get_test_letters(self) -> Dict[str, str]:
        """Get standardized test letters matching test plan specifications."""
        return {
            "high_quality": """
[Professional Medical Associates]
1234 Medical Center Drive, Suite 200
Springfield, VA 22150
Phone: (703) 555-0123

Date: November 15, 2024

RE: Nexus Letter for Veteran John M. Smith
Service Number: 123-45-6789
Date of Birth: January 15, 1980

To Whom It May Concern:

I am Dr. Sarah Johnson, MD, a board-certified orthopedic surgeon with over 20 years of experience treating military personnel and veterans. I hold medical license #VA12345 and am currently practicing at Professional Medical Associates.

After conducting a comprehensive examination of Mr. John M. Smith and thoroughly reviewing his military service records, medical history, and current clinical presentation, it is my professional medical opinion that it is at least as likely as not (greater than 50% probability) that Mr. Smith's current lumbar spine condition is causally related to the documented back injury he sustained during his military service in Afghanistan.

MEDICAL RATIONALE:
The medical basis for this opinion is supported by several key factors:

1. TEMPORAL RELATIONSHIP: Mr. Smith's service medical records document a specific back injury occurring on March 15, 2005, during a convoy operation when his vehicle struck an IED. He was immediately treated at the forward operating base and later at Landstuhl Regional Medical Center.

2. CLINICAL CORRELATION: Current MRI findings show L4-L5 disc herniation with associated spinal stenosis, which is consistent with the type of traumatic injury documented in his service records. The pattern of degeneration is characteristic of post-traumatic changes rather than age-related wear.

3. SYMPTOM CONTINUITY: Medical records demonstrate continuous treatment for back pain from the time of service injury through his current presentation, with no significant intervening trauma or alternative causative factors.

4. MEDICAL LITERATURE SUPPORT: Current medical literature, including studies published in the Journal of Spinal Disorders and the American Journal of Physical Medicine, establishes that high-energy trauma such as IED blasts frequently result in spinal injuries that progress to chronic degenerative changes.

CONCLUSION:
Based on the documented service-connected trauma, the temporal relationship between service injury and current symptoms, clinical findings consistent with post-traumatic spinal degeneration, and the absence of intervening causes, it is my medical opinion that Mr. Smith's lumbar spine condition is at least as likely as not (≥50% probability) causally related to his military service.

If you have any questions regarding this assessment, please feel free to contact my office.

Sincerely,

Sarah Johnson, MD
Board Certified Orthopedic Surgeon
Virginia Medical License #VA12345
Phone: (703) 555-0123
""",
            "medium_quality": """
Date: November 15, 2024

To Whom It May Concern:

I have examined veteran John Smith for his back condition. Based on my review of his service history and current symptoms, I believe his lumbar spine problems are probably related to his military service.

The veteran reports injuring his back during service in Afghanistan in 2005. He has had ongoing back pain since that time. Current examination shows signs of lumbar spine disease.

In my opinion, there is a reasonable connection between his service injury and current condition.

Dr. Michael Brown, MD
Internal Medicine
""",
            "poor_quality": """
The veteran says his back hurts and he thinks it started in the military. Based on what he told me, I agree it could be related to his service.

Dr. Jones
""",
        }

    def run_all_tests(self) -> Dict[str, Any]:
        """Execute complete test suite."""
        print("=== MILESTONE 2 COMPREHENSIVE TEST EXECUTION ===\n")
        print(
            f"Test execution started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}"
        )

        try:
            # Phase 1: Component Testing
            self.test_scoring_engine_validation()
            self.test_recommendation_engine()
            self.test_database_integration()

            # Phase 2: Integration Testing
            self.test_enhanced_ui_integration()
            self.test_end_to_end_workflow()

            # Phase 3: Professional Validation
            self.test_professional_presentation()
            self.test_performance_and_analytics()

            # Generate summary
            return self.generate_test_summary()

        except Exception as e:
            self.log_test("CRITICAL_ERROR", False, f"Test execution failed: {str(e)}")
            import traceback

            print(f"\nCritical error during testing:\n{traceback.format_exc()}")
            return {}

    def test_scoring_engine_validation(self):
        """TEST-2.1.x: Scoring Engine Validation Tests."""
        print("\n=== PHASE 1: SCORING ENGINE VALIDATION ===")

        scorer = create_scorer()
        analyzer = create_analyzer()
        processor = create_processor()
        letters = self.get_test_letters()

        # TEST-2.1.1: Medical Opinion Scoring Consistency
        print("\nTEST-2.1.1: Medical Opinion Scoring Consistency")

        high_quality_letter = letters["high_quality"]
        scores = []

        for i in range(5):
            processed_text = processor.preprocess_for_ai(high_quality_letter)
            ai_results = analyzer.analyze_letter(processed_text)

            if ai_results.get("error"):
                self.log_test("TEST-2.1.1", False, f"AI analysis failed on run {i+1}")
                continue

            scoring_results = scorer.calculate_total_score(ai_results["analysis"])
            medical_score = scoring_results.get("medical_opinion_breakdown")

            if medical_score and hasattr(medical_score, "score"):
                scores.append(medical_score.score)

            time.sleep(1)  # Brief pause between requests

        if len(scores) >= 5:
            score_variance = statistics.variance(scores) if len(scores) > 1 else 0
            consistency_passed = score_variance == 0
            avg_score = statistics.mean(scores)

            self.log_test(
                "TEST-2.1.1",
                consistency_passed,
                f"Score variance: {score_variance}, Average: {avg_score:.1f}, Scores: {scores}",
            )

            # Verify high-quality letter scores highly
            high_score_passed = avg_score >= 20
            self.log_test(
                "TEST-2.1.1-Quality",
                high_score_passed,
                f"High-quality letter average score: {avg_score:.1f}/25 (expected ≥20)",
            )
        else:
            self.log_test("TEST-2.1.1", False, "Insufficient valid scores obtained")

        # TEST-2.1.2: Service Connection Scoring Accuracy
        print("\nTEST-2.1.2: Service Connection Scoring Accuracy")

        test_cases = [
            (letters["high_quality"], 18, 25, "High quality with explicit connection"),
            (letters["medium_quality"], 10, 17, "Medium quality with basic connection"),
            (letters["poor_quality"], 0, 9, "Poor quality with minimal connection"),
        ]

        for letter, min_expected, max_expected, description in test_cases:
            processed_text = processor.preprocess_for_ai(letter)
            ai_results = analyzer.analyze_letter(processed_text)

            if not ai_results.get("error"):
                scoring_results = scorer.calculate_total_score(ai_results["analysis"])
                service_score = scoring_results.get("service_connection_breakdown")

                if service_score and hasattr(service_score, "score"):
                    score = service_score.score
                    score_in_range = min_expected <= score <= max_expected
                    self.log_test(
                        "TEST-2.1.2",
                        score_in_range,
                        f"{description}: {score}/25 (expected {min_expected}-{max_expected})",
                    )
                else:
                    self.log_test(
                        "TEST-2.1.2",
                        False,
                        f"No service connection score for {description}",
                    )
            else:
                self.log_test(
                    "TEST-2.1.2", False, f"AI analysis failed for {description}"
                )

        # TEST-2.1.3: Overall Score Calculation
        print("\nTEST-2.1.3: Overall Score Calculation")

        processed_text = processor.preprocess_for_ai(letters["high_quality"])
        ai_results = analyzer.analyze_letter(processed_text)

        if not ai_results.get("error"):
            scoring_results = scorer.calculate_total_score(ai_results["analysis"])

            # Extract component scores
            components = [
                "medical_opinion",
                "service_connection",
                "medical_rationale",
                "professional_format",
            ]
            component_scores = []

            for comp in components:
                breakdown = scoring_results.get(f"{comp}_breakdown")
                if breakdown and hasattr(breakdown, "score"):
                    component_scores.append(breakdown.score)

            if len(component_scores) == 4:
                calculated_total = sum(component_scores)
                reported_total = scoring_results.get("overall_score", 0)

                calculation_correct = calculated_total == reported_total
                score_in_range = 0 <= reported_total <= 100

                self.log_test(
                    "TEST-2.1.3-Math",
                    calculation_correct,
                    f"Components sum: {calculated_total}, Reported: {reported_total}",
                )
                self.log_test(
                    "TEST-2.1.3-Range",
                    score_in_range,
                    f"Overall score {reported_total} within 0-100 range",
                )
            else:
                self.log_test(
                    "TEST-2.1.3", False, "Could not extract all component scores"
                )
        else:
            self.log_test("TEST-2.1.3", False, "AI analysis failed")

        # TEST-2.1.4: Repeatability Validation
        print("\nTEST-2.1.4: Repeatability Validation")

        repeat_scores = []
        repeat_recommendations = []

        for i in range(3):  # Reduced to 3 for API efficiency
            processed_text = processor.preprocess_for_ai(letters["medium_quality"])
            ai_results = analyzer.analyze_letter(processed_text)

            if not ai_results.get("error"):
                scoring_results = scorer.calculate_total_score(ai_results["analysis"])
                overall_score = scoring_results.get("overall_score", 0)
                repeat_scores.append(overall_score)

                # Get recommendation
                rec_engine = create_recommendation_engine()
                recommendations = rec_engine.generate_recommendations(
                    overall_score, scoring_results, ai_results["analysis"]
                )

                workflow_rec = recommendations.get("workflow_recommendation")
                if workflow_rec and hasattr(workflow_rec, "decision"):
                    repeat_recommendations.append(workflow_rec.decision)

            time.sleep(1)

        if len(repeat_scores) >= 3:
            score_variance = (
                statistics.variance(repeat_scores) if len(repeat_scores) > 1 else 0
            )
            score_consistency = (
                score_variance < 5
            )  # Allow small variance due to AI variability

            recommendation_consistency = len(set(repeat_recommendations)) <= 1

            self.log_test(
                "TEST-2.1.4-Scores",
                score_consistency,
                f"Score variance: {score_variance:.2f}, Scores: {repeat_scores}",
            )
            self.log_test(
                "TEST-2.1.4-Recommendations",
                recommendation_consistency,
                f"Recommendation consistency: {repeat_recommendations}",
            )
        else:
            self.log_test("TEST-2.1.4", False, "Insufficient repeat test results")

    def test_recommendation_engine(self):
        """TEST-2.2.x: Recommendation Engine Tests."""
        print("\n=== RECOMMENDATION ENGINE TESTS ===")

        rec_engine = create_recommendation_engine()

        # TEST-2.2.1: Decision Threshold Accuracy
        print("\nTEST-2.2.1: Decision Threshold Accuracy")

        test_scenarios = [
            (90, "auto_approve", "High score should auto-approve"),
            (75, "attorney_review", "Medium score should require attorney review"),
            (50, "revision_required", "Low score should require revision"),
        ]

        for score, expected_decision, description in test_scenarios:
            # Create mock analysis data
            mock_analysis = {
                "nexus_strength": (
                    "Strong" if score >= 85 else "Moderate" if score >= 70 else "Weak"
                ),
                "primary_condition": "Test Condition",
                "key_strengths": ["Test strength"],
                "critical_issues": [] if score >= 70 else ["Test issue"],
            }

            mock_scoring = {
                "overall_score": score,
                "medical_opinion_breakdown": type(
                    "obj", (object,), {"score": score // 4, "max_score": 25}
                ),
                "service_connection_breakdown": type(
                    "obj", (object,), {"score": score // 4, "max_score": 25}
                ),
                "medical_rationale_breakdown": type(
                    "obj", (object,), {"score": score // 4, "max_score": 25}
                ),
                "professional_format_breakdown": type(
                    "obj", (object,), {"score": score // 4, "max_score": 25}
                ),
            }

            recommendations = rec_engine.generate_recommendations(
                score, mock_scoring, mock_analysis
            )
            workflow_rec = recommendations.get("workflow_recommendation")

            if workflow_rec and hasattr(workflow_rec, "decision"):
                decision_correct = workflow_rec.decision == expected_decision
                self.log_test(
                    "TEST-2.2.1",
                    decision_correct,
                    f"{description}: Score {score} → {workflow_rec.decision} (expected {expected_decision})",
                )
            else:
                self.log_test(
                    "TEST-2.2.1", False, f"No workflow recommendation for score {score}"
                )

    def test_database_integration(self):
        """TEST-2.3.x: Database Integration Tests."""
        print("\n=== DATABASE INTEGRATION TESTS ===")

        database = create_database(self.test_db_path)

        # TEST-2.3.1: Analysis Storage Integrity
        print("\nTEST-2.3.1: Analysis Storage Integrity")

        # Create sample analysis data
        sample_letter = self.get_test_letters()["medium_quality"]

        analyzer = create_analyzer()
        scorer = create_scorer()
        rec_engine = create_recommendation_engine()
        processor = create_processor()

        processed_text = processor.preprocess_for_ai(sample_letter)
        ai_results = analyzer.analyze_letter(processed_text)

        if not ai_results.get("error"):
            scoring_results = scorer.calculate_total_score(ai_results["analysis"])
            recommendations = rec_engine.generate_recommendations(
                scoring_results["overall_score"],
                scoring_results,
                ai_results["analysis"],
            )

            # Store analysis
            analysis_id = database.save_analysis(
                sample_letter,
                ai_results["analysis"],
                scoring_results,
                recommendations,
                2.5,
            )

            # Retrieve and verify
            retrieved = database.get_analysis(analysis_id)

            if retrieved:
                # Check key fields
                storage_integrity = (
                    retrieved["overall_score"] == scoring_results["overall_score"]
                    and retrieved["workflow_decision"]
                    in ["auto_approve", "attorney_review", "revision_required"]
                    and retrieved["processing_time_seconds"] == 2.5
                )

                self.log_test(
                    "TEST-2.3.1",
                    storage_integrity,
                    f"Analysis ID {analysis_id}: Score {retrieved['overall_score']}, Decision {retrieved['workflow_decision']}",
                )
            else:
                self.log_test(
                    "TEST-2.3.1", False, f"Could not retrieve analysis ID {analysis_id}"
                )
        else:
            self.log_test("TEST-2.3.1", False, "AI analysis failed for storage test")

        # TEST-2.3.3: Metrics Calculation Accuracy
        print("\nTEST-2.3.3: Metrics Calculation Accuracy")

        # Create multiple analyses for metrics testing
        letters = self.get_test_letters()
        stored_scores = []

        for i, (quality, letter) in enumerate(letters.items()):
            processed_text = processor.preprocess_for_ai(letter)
            ai_results = analyzer.analyze_letter(processed_text)

            if not ai_results.get("error"):
                scoring_results = scorer.calculate_total_score(ai_results["analysis"])
                recommendations = rec_engine.generate_recommendations(
                    scoring_results["overall_score"],
                    scoring_results,
                    ai_results["analysis"],
                )

                database.save_analysis(
                    letter,
                    ai_results["analysis"],
                    scoring_results,
                    recommendations,
                    1.0 + i,
                )

                stored_scores.append(scoring_results["overall_score"])
                time.sleep(0.5)

        if stored_scores:
            # Test analytics calculations
            analytics = AnalyticsEngine(database)
            metrics = analytics.get_summary_metrics(days=1)

            expected_avg = statistics.mean(stored_scores)
            reported_avg = metrics["avg_score"]
            expected_total = len(stored_scores)
            reported_total = metrics["total_analyses"]

            avg_accuracy = abs(expected_avg - reported_avg) < 1.0
            count_accuracy = expected_total == reported_total

            self.log_test(
                "TEST-2.3.3-Average",
                avg_accuracy,
                f"Expected avg: {expected_avg:.1f}, Reported: {reported_avg:.1f}",
            )
            self.log_test(
                "TEST-2.3.3-Count",
                count_accuracy,
                f"Expected count: {expected_total}, Reported: {reported_total}",
            )
        else:
            self.log_test("TEST-2.3.3", False, "No analyses stored for metrics testing")

    def test_enhanced_ui_integration(self):
        """TEST-2.4.x: Enhanced UI Integration Tests."""
        print("\n=== ENHANCED UI INTEGRATION TESTS ===")

        # These tests verify the UI components work without visual validation
        # In a full implementation, these would include screenshot testing

        # TEST-2.4.1: Component Integration
        print("\nTEST-2.4.1: UI Component Integration")

        try:
            # Test that all UI components can be imported and initialized
            from analytics import display_analytics_dashboard

            database = create_database(self.test_db_path)

            # Verify analytics dashboard function exists and is callable
            ui_components_available = callable(display_analytics_dashboard)
            self.log_test(
                "TEST-2.4.1",
                ui_components_available,
                "Analytics dashboard component available",
            )

        except ImportError as e:
            self.log_test("TEST-2.4.1", False, f"UI component import failed: {str(e)}")

    def test_end_to_end_workflow(self):
        """TEST-2.5.x: End-to-End Workflow Tests."""
        print("\n=== END-TO-END WORKFLOW TESTS ===")

        # TEST-2.5.1: Complete Enhanced Workflow
        print("\nTEST-2.5.1: Complete Enhanced Workflow")

        workflow_start = time.time()

        try:
            # Initialize all components
            processor = create_processor()
            analyzer = create_analyzer()
            scorer = create_scorer()
            rec_engine = create_recommendation_engine()
            database = create_database(self.test_db_path)

            # Process sample letter through complete workflow
            sample_letter = self.get_test_letters()["high_quality"]

            # Step 1: Text processing
            processed_text = processor.preprocess_for_ai(sample_letter)

            # Step 2: AI analysis
            ai_results = analyzer.analyze_letter(processed_text)
            workflow_step2_success = not ai_results.get("error")

            # Step 3: Scoring
            if workflow_step2_success:
                scoring_results = scorer.calculate_total_score(ai_results["analysis"])
                workflow_step3_success = "overall_score" in scoring_results
            else:
                workflow_step3_success = False

            # Step 4: Recommendations
            if workflow_step3_success:
                recommendations = rec_engine.generate_recommendations(
                    scoring_results["overall_score"],
                    scoring_results,
                    ai_results["analysis"],
                )
                workflow_step4_success = "workflow_recommendation" in recommendations
            else:
                workflow_step4_success = False

            # Step 5: Database storage
            if workflow_step4_success:
                processing_time = time.time() - workflow_start
                analysis_id = database.save_analysis(
                    sample_letter,
                    ai_results["analysis"],
                    scoring_results,
                    recommendations,
                    processing_time,
                )
                workflow_step5_success = analysis_id is not None
            else:
                workflow_step5_success = False

            # Step 6: Analytics update
            if workflow_step5_success:
                analytics = AnalyticsEngine(database)
                metrics = analytics.get_summary_metrics()
                workflow_step6_success = metrics["total_analyses"] > 0
            else:
                workflow_step6_success = False

            total_workflow_time = time.time() - workflow_start

            complete_workflow_success = all(
                [
                    workflow_step2_success,
                    workflow_step3_success,
                    workflow_step4_success,
                    workflow_step5_success,
                    workflow_step6_success,
                ]
            )

            self.log_test(
                "TEST-2.5.1",
                complete_workflow_success,
                f"Complete workflow in {total_workflow_time:.2f}s",
            )

            # Performance requirement check
            performance_acceptable = total_workflow_time < 30.0
            self.log_test(
                "TEST-2.5.1-Performance",
                performance_acceptable,
                f"Workflow completed in {total_workflow_time:.2f}s (requirement: <30s)",
            )

        except Exception as e:
            self.log_test("TEST-2.5.1", False, f"Workflow failed: {str(e)}")

    def test_professional_presentation(self):
        """TEST-2.6.x: Professional Presentation Tests."""
        print("\n=== PROFESSIONAL PRESENTATION TESTS ===")

        # TEST-2.6.1: Output Professional Quality
        print("\nTEST-2.6.1: Output Professional Quality")

        try:
            # Generate analysis results
            analyzer = create_analyzer()
            scorer = create_scorer()
            rec_engine = create_recommendation_engine()
            processor = create_processor()

            sample_letter = self.get_test_letters()["high_quality"]
            processed_text = processor.preprocess_for_ai(sample_letter)
            ai_results = analyzer.analyze_letter(processed_text)

            if not ai_results.get("error"):
                scoring_results = scorer.calculate_total_score(ai_results["analysis"])
                recommendations = rec_engine.generate_recommendations(
                    scoring_results["overall_score"],
                    scoring_results,
                    ai_results["analysis"],
                )

                # Check professional language in recommendations
                client_summary = recommendations.get("client_summary", "")
                workflow_rec = recommendations.get("workflow_recommendation")

                # Basic professionalism checks
                professional_checks = []

                # Check for professional language (no casual terms)
                casual_terms = ["awesome", "cool", "super", "totally", "kinda", "sorta"]
                has_casual_language = any(
                    term in client_summary.lower() for term in casual_terms
                )
                professional_checks.append(not has_casual_language)

                # Check for clear structure
                has_clear_structure = (
                    "**" in client_summary or "Score:" in client_summary
                )
                professional_checks.append(has_clear_structure)

                # Check for actionable recommendations
                has_recommendations = workflow_rec and hasattr(
                    workflow_rec, "next_steps"
                )
                professional_checks.append(has_recommendations)

                professional_quality = all(professional_checks)

                self.log_test(
                    "TEST-2.6.1",
                    professional_quality,
                    f"Professional quality checks: {sum(professional_checks)}/3 passed",
                )
            else:
                self.log_test(
                    "TEST-2.6.1", False, "Could not generate output for quality testing"
                )

        except Exception as e:
            self.log_test(
                "TEST-2.6.1", False, f"Professional presentation test failed: {str(e)}"
            )

    def test_performance_and_analytics(self):
        """TEST-2.7: Performance and Analytics Tests."""
        print("\n=== PERFORMANCE AND ANALYTICS TESTS ===")

        database = create_database(self.test_db_path)
        analytics = AnalyticsEngine(database)

        # Test analytics calculations
        print("\nTEST-2.7.1: Analytics Performance")

        try:
            analytics_start = time.time()

            # Get various analytics metrics
            summary_metrics = analytics.get_summary_metrics()
            roi_metrics = analytics.get_roi_metrics()
            quality_metrics = analytics.get_quality_metrics()

            analytics_time = time.time() - analytics_start

            # Check that analytics complete quickly
            analytics_fast = analytics_time < 5.0

            # Check that metrics contain expected fields
            required_summary_fields = [
                "total_analyses",
                "avg_score",
                "auto_approve_rate",
            ]
            summary_complete = all(
                field in summary_metrics for field in required_summary_fields
            )

            required_roi_fields = ["net_savings", "roi_percentage", "efficiency_gain"]
            roi_complete = all(field in roi_metrics for field in required_roi_fields)

            self.log_test(
                "TEST-2.7.1-Speed",
                analytics_fast,
                f"Analytics computed in {analytics_time:.2f}s",
            )
            self.log_test(
                "TEST-2.7.1-Summary",
                summary_complete,
                f"Summary metrics complete: {list(summary_metrics.keys())}",
            )
            self.log_test(
                "TEST-2.7.1-ROI",
                roi_complete,
                f"ROI metrics complete: {list(roi_metrics.keys())}",
            )

        except Exception as e:
            self.log_test("TEST-2.7.1", False, f"Analytics test failed: {str(e)}")

    def generate_test_summary(self) -> Dict[str, bool]:
        """Generate comprehensive test summary."""
        print("\n" + "=" * 60)
        print("MILESTONE 2 TEST EXECUTION SUMMARY")
        print("=" * 60)

        # Calculate overall statistics
        total_tests = sum(len(results) for results in self.results.values())
        passed_tests = sum(sum(results) for results in self.results.values())

        execution_time = datetime.now() - self.start_time

        print(f"Execution Time: {execution_time}")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(
            f"Success Rate: {(passed_tests/total_tests*100):.1f}%"
            if total_tests > 0
            else "0%"
        )

        # Detailed results by category
        print(f"\nDETAILED RESULTS:")
        print("-" * 40)

        category_results = {}
        for test_name, results in self.results.items():
            category = test_name.split("-")[0] if "-" in test_name else test_name
            if category not in category_results:
                category_results[category] = {"passed": 0, "total": 0}

            category_results[category]["total"] += len(results)
            category_results[category]["passed"] += sum(results)

        for category, stats in category_results.items():
            success_rate = (
                (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
            )
            print(
                f"{category}: {stats['passed']}/{stats['total']} ({success_rate:.1f}%)"
            )

        print(f"\nFULL TEST LOG:")
        print("-" * 40)
        for log_entry in self.test_log:
            print(log_entry)

        # Return summary for validation log
        return {
            "total_tests": total_tests,  # type: ignore[dict-item]
            "passed_tests": passed_tests,  # type: ignore[dict-item]
            "success_rate": (  # type: ignore[dict-item]
                (passed_tests / total_tests * 100) if total_tests > 0 else 0
            ),
            "execution_time": str(execution_time),  # type: ignore[dict-item]
            "category_results": category_results,  # type: ignore[dict-item]
        }


if __name__ == "__main__":
    runner = Milestone2TestRunner()
    summary = runner.run_all_tests()

    print(f"\n{'='*60}")
    print(f"MILESTONE 2 TESTING COMPLETE")
    print(f"Overall Success Rate: {summary.get('success_rate', 0):.1f}%")
    print(f"{'='*60}")
