"""Demo script to show current analysis functionality."""

from ai_analyzer import create_analyzer
import json

# Sample nexus letter
test_letter = """
Veterans Medical Center
123 Main Street
Houston, TX 77001

March 20, 2024

RE: Nexus Letter for James Wilson, SSN: XXX-XX-1234

To Whom It May Concern,

I am Dr. Robert Martinez, M.D., board-certified orthopedic surgeon with 20 years of experience. I have been treating Mr. Wilson for chronic lower back pain and bilateral knee conditions since January 2023.

Based on my comprehensive medical evaluation, review of Mr. Wilson's service medical records, and current medical literature, it is at least as likely as not (50% or greater probability) that Mr. Wilson's current lumbar spine condition and bilateral knee osteoarthritis are directly related to his military service.

Mr. Wilson served as an infantry soldier from 2003-2011, including two deployments to Iraq. His duties required carrying heavy equipment (often exceeding 80 pounds), jumping from vehicles, and sustained physical stress. His service medical records document multiple complaints of back and knee pain during service.

The medical rationale for this opinion includes:
1. Documented in-service injuries and complaints
2. Continuity of symptomatology since service
3. Current imaging showing degenerative changes consistent with repetitive trauma
4. Medical literature supporting the connection between military service activities and these conditions

I am available for any questions regarding this medical opinion.

Sincerely,
Dr. Robert Martinez, M.D.
Board Certified Orthopedic Surgeon
License #: TX-12345
Phone: (555) 123-4567
"""

def demonstrate_current_analysis():
    """Show what the current analysis provides."""
    print("🔍 CURRENT NEXUS LETTER ANALYZER FUNCTIONALITY")
    print("=" * 60)
    print("\nAnalyzing sample nexus letter...")
    print("-" * 60)
    
    try:
        analyzer = create_analyzer()
        result = analyzer.analyze_letter(test_letter)
        
        if not result.get("error"):
            analysis = result["analysis"]
            
            print("\n✅ ANALYSIS RESULTS (What you get NOW in Milestone 1):\n")
            
            print(f"📊 NEXUS STRENGTH: {analysis['nexus_strength']}")
            print(f"   - Medical Opinion Present: {analysis['medical_opinion_present']}")
            print(f"   - Service Connection Stated: {analysis['service_connection_stated']}")
            print(f"   - Medical Rationale Provided: {analysis['medical_rationale_provided']}")
            
            print(f"\n🏥 MEDICAL DETAILS:")
            print(f"   - Primary Condition: {analysis['primary_condition']}")
            print(f"   - Service Connected To: {analysis['service_connected_condition']}")
            print(f"   - Connection Type: {analysis['connection_theory']}")
            print(f"   - Probability Statement: {analysis['probability_rating']}")
            
            print(f"\n💪 STRENGTHS:")
            for i, strength in enumerate(analysis['strengths'], 1):
                print(f"   {i}. {strength}")
            
            print(f"\n⚠️  WEAKNESSES/AREAS FOR IMPROVEMENT:")
            for i, weakness in enumerate(analysis['weaknesses'], 1):
                print(f"   {i}. {weakness}")
            
            print(f"\n📝 RECOMMENDATIONS:")
            for i, rec in enumerate(analysis['recommendations'], 1):
                print(f"   {i}. {rec}")
            
            print(f"\n📋 SUMMARY:")
            print(f"   {analysis['summary']}")
            
            print("\n" + "=" * 60)
            print("🎯 This comprehensive analysis is available RIGHT NOW!")
            print("   Just paste a letter and click 'Analyze Letter'")
            
        else:
            print(f"❌ Error: {result['message']}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    demonstrate_current_analysis()