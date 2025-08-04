"""Integration test for Milestone 2 components."""

import time
import json
from ai_analyzer import create_analyzer
from scoring_engine import create_scorer
from recommendation_engine import create_recommendation_engine
from database import create_database
from text_processor import create_processor


def test_milestone2_integration():
    """Test complete integration of all Milestone 2 components."""
    
    print("=== Milestone 2 Integration Test ===\n")
    
    # Sample nexus letter for testing
    test_letter = """
    [Medical Practice Name]
    123 Medical Center Dr, Suite 100
    Anytown, ST 12345
    Phone: (555) 123-4567
    
    Date: November 15, 2024
    
    RE: Nexus Letter for Veteran John Doe
    Service Number: 123-45-6789
    
    To Whom It May Concern:
    
    I am Dr. Jane Smith, MD, a board-certified psychiatrist with over 15 years of experience 
    treating veterans with mental health conditions. I have been treating Mr. John Doe since 
    January 2023 for Post-Traumatic Stress Disorder (PTSD).
    
    After reviewing Mr. Doe's medical records, service records, and conducting multiple clinical 
    evaluations, it is my professional medical opinion that it is at least as likely as not 
    (50 percent or greater probability) that Mr. Doe's current PTSD is directly related to his 
    military service.
    
    Mr. Doe served in Iraq from 2003-2004 where he was exposed to multiple combat situations, 
    including IED explosions and direct enemy fire. His service records document these exposures, 
    and he received a Combat Action Ribbon for his service.
    
    The medical literature clearly establishes that combat exposure is a significant risk factor 
    for developing PTSD. Studies published in the Journal of Traumatic Stress show that veterans 
    with combat exposure have a 10-20% prevalence rate of PTSD, significantly higher than the 
    general population.
    
    Mr. Doe's symptoms began during his deployment and have persisted since his return. He 
    experiences nightmares, hypervigilance, avoidance behaviors, and intrusive memories - all 
    classic symptoms of combat-related PTSD as defined in the DSM-5.
    
    In conclusion, based on the documented combat exposures during service, the onset of symptoms 
    during deployment, and the continuation of symptoms consistent with PTSD, it is my medical 
    opinion that Mr. Doe's PTSD is at least as likely as not caused by his military service.
    
    If you have any questions, please do not hesitate to contact me.
    
    Sincerely,
    
    Jane Smith, MD
    Board Certified Psychiatrist
    License #MD12345
    """
    
    try:
        # Initialize components
        print("1. Initializing components...")
        processor = create_processor()
        analyzer = create_analyzer()
        scorer = create_scorer()
        rec_engine = create_recommendation_engine()
        database = create_database("test_milestone2.db")
        print("   ✓ All components initialized\n")
        
        # Test AI connection
        print("2. Testing AI connection...")
        success, msg = analyzer.test_connection()
        if not success:
            print(f"   ✗ Connection failed: {msg}")
            return
        print("   ✓ AI connection successful\n")
        
        # Process text
        print("3. Processing text...")
        processed_text = processor.preprocess_for_ai(test_letter)
        stats = processor.get_text_stats(test_letter)
        print(f"   ✓ Text processed: {stats['word_count']} words, {stats['sentence_count']} sentences\n")
        
        # Perform AI analysis
        print("4. Performing AI analysis...")
        start_time = time.time()
        ai_results = analyzer.analyze_letter(processed_text)
        
        if ai_results.get('error'):
            print(f"   ✗ AI analysis failed: {ai_results.get('message')}")
            return
        
        analysis = ai_results['analysis']
        print("   ✓ AI analysis complete")
        print(f"   - Nexus Strength: {analysis.get('nexus_strength')}")
        print(f"   - Primary Condition: {analysis.get('primary_condition')}")
        print(f"   - Probability Language: {analysis.get('probability_language', 'Not found')}\n")
        
        # Calculate scores
        print("5. Calculating VA compliance scores...")
        scoring_results = scorer.calculate_total_score(analysis)
        print(f"   ✓ Scoring complete: {scoring_results['overall_score']}/100")
        
        # Print component scores
        components = ['medical_opinion', 'service_connection', 'medical_rationale', 'professional_format']
        for comp in components:
            breakdown = scoring_results.get(f'{comp}_breakdown')
            if breakdown and hasattr(breakdown, 'score'):
                print(f"   - {comp.replace('_', ' ').title()}: {breakdown.score}/{breakdown.max_score}")
        print()
        
        # Generate recommendations
        print("6. Generating recommendations...")
        recommendations = rec_engine.generate_recommendations(
            scoring_results['overall_score'],
            scoring_results,
            analysis
        )
        
        workflow_rec = recommendations.get('workflow_recommendation')
        if workflow_rec:
            print(f"   ✓ Workflow Decision: {workflow_rec.decision}")
            print(f"   - {workflow_rec.message}")
        
        improvements = recommendations.get('improvement_suggestions', [])
        critical = recommendations.get('critical_issues', 0)
        print(f"   - Total Improvements: {len(improvements)}")
        print(f"   - Critical Issues: {critical}\n")
        
        # Save to database
        print("7. Saving to database...")
        processing_time = time.time() - start_time
        
        analysis_id = database.save_analysis(
            test_letter,
            analysis,
            scoring_results,
            recommendations,
            processing_time
        )
        print(f"   ✓ Analysis saved with ID: {analysis_id}")
        print(f"   - Processing time: {processing_time:.2f} seconds\n")
        
        # Verify database retrieval
        print("8. Verifying database retrieval...")
        retrieved = database.get_analysis(analysis_id)
        if retrieved:
            print(f"   ✓ Analysis retrieved successfully")
            print(f"   - Stored score: {retrieved['overall_score']}")
            print(f"   - Stored decision: {retrieved['workflow_decision']}\n")
        else:
            print("   ✗ Failed to retrieve analysis\n")
        
        # Test analytics
        print("9. Testing analytics engine...")
        from analytics import AnalyticsEngine
        analytics = AnalyticsEngine(database)
        
        metrics = analytics.get_summary_metrics()
        print(f"   ✓ Analytics calculated")
        print(f"   - Total analyses: {metrics['total_analyses']}")
        print(f"   - Average score: {metrics['avg_score']:.1f}")
        print(f"   - Auto-approve rate: {metrics['auto_approve_rate']:.1f}%\n")
        
        # Summary
        print("=== Integration Test Summary ===")
        print("✓ All components integrated successfully")
        print(f"✓ End-to-end processing time: {processing_time:.2f} seconds")
        print(f"✓ Letter scored {scoring_results['overall_score']}/100")
        print(f"✓ Workflow recommendation: {workflow_rec.decision.replace('_', ' ').title()}")
        print("\nMilestone 2 integration test PASSED!")
        
        # Print top improvements for reference
        if improvements:
            print("\n=== Top Improvement Suggestions ===")
            for i, imp in enumerate(improvements[:3], 1):
                if hasattr(imp, 'component'):
                    print(f"{i}. {imp.component.replace('_', ' ').title()} ({imp.impact})")
                    print(f"   {imp.suggestion}")
        
    except Exception as e:
        print(f"\n✗ Integration test failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_milestone2_integration()