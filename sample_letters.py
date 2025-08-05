"""Professional demonstration data for Nexus Letter AI Analyzer.

This module provides high-quality sample letters, demonstration scenarios,
and talking points for professional presentation of the AI analysis system.
"""

from typing import Dict, List, Tuple

STRONG_NEXUS_LETTER = """
University Medical Center
Department of Cardiology
123 Medical Drive
Anytown, ST 12345

January 15, 2024

RE: Nexus Letter for John D. Veteran, DOB: 03/15/1975

To Whom It May Concern,

I am Dr. Sarah Johnson, M.D., a board-certified cardiologist with 15 years of experience in cardiovascular medicine. I have been treating Mr. John D. Veteran since September 2023 for coronary artery disease and have thoroughly reviewed his complete medical records, military service records, and C&P examination reports.

MEDICAL HISTORY AND SERVICE CONNECTION:

Mr. Veteran served in the U.S. Army from 1995-2015, including three deployments to Iraq and Afghanistan. During his service, he was exposed to significant cardiovascular stressors including:
- Prolonged exposure to burn pits and environmental toxins
- High-stress combat operations
- Sleep deprivation and irregular schedules
- Physical demands of military service

Based on my comprehensive evaluation and review of current medical literature regarding environmental exposures during military service, I find a clear connection between Mr. Veteran's current coronary artery disease and his military service.

MEDICAL OPINION:

In my professional medical opinion, based on a reasonable degree of medical certainty, it is at least as likely as not (greater than 50% probability) that Mr. Veteran's coronary artery disease is directly related to his military service exposures, particularly his exposure to burn pit toxins and prolonged cardiovascular stress during combat operations.

The medical literature supports the connection between environmental toxin exposure and accelerated cardiovascular disease. Mr. Veteran's coronary artery disease manifested at an unusually young age (48 years old) without traditional risk factors, which is consistent with environmental exposure-related cardiovascular disease.

MEDICAL RATIONALE:

The pathophysiological mechanism involves chronic inflammatory responses triggered by toxin exposure leading to accelerated atherosclerosis. This is supported by:
1. Elevated inflammatory markers in Mr. Veteran's laboratory studies
2. Absence of significant family history of early cardiac disease  
3. Timeline correlation between service exposure and symptom onset
4. Pattern of disease consistent with environmental exposure

I am available to provide further clarification or testimony regarding this medical opinion.

Sincerely,

Dr. Sarah Johnson, M.D.
Board Certified Cardiologist
License #: MD123456
"""

MODERATE_NEXUS_LETTER = """
Community Health Clinic
456 Health Street
Hometown, ST 67890

February 8, 2024

RE: Medical Opinion for Robert Smith

Dear VA Rating Official,

I am Dr. Michael Brown, MD, and I have been treating Mr. Robert Smith for chronic lower back pain since 2022. I have reviewed his military records and medical history.

Mr. Smith served in the Marines for 8 years and experienced a back injury during training in 2010. He has ongoing pain and mobility issues.

Based on my examination and review of records, I believe there is a connection between his current back condition and his military service injury. The injury he sustained during training appears to have led to his current chronic condition.

In my medical opinion, it is likely that Mr. Smith's current back problems are related to his military service. The timeline matches up and his symptoms are consistent with the original injury.

I recommend continued treatment for his condition.

Respectfully,

Dr. Michael Brown, MD
Internal Medicine
"""

WEAK_NEXUS_LETTER = """
Medical Associates
789 Doctor Lane
Smalltown, ST 11111

March 3, 2024

To Whom It May Concern,

I have seen Mr. William Davis a few times for knee pain. He mentioned he was in the military and hurt his knee.

His knee hurts and he has some swelling. I think it might be related to his time in service but I'm not completely sure. There could be other causes too.

He should continue taking pain medication and maybe do some physical therapy.

Dr. Lisa White
General Practice
"""

# Dictionary for easy access
SAMPLE_LETTERS = {
    "strong": {
        "title": "Strong Nexus Letter - Coronary Artery Disease",
        "description": "Well-structured letter with clear medical opinion, detailed rationale, and proper probability language",
        "text": STRONG_NEXUS_LETTER,
        "expected_strength": "Strong",
        "key_features": [
            "Clear probability statement (>50%)",
            "Detailed medical rationale",
            "Service connection well-established",
            "Board-certified physician",
            "Literature references",
            "Professional formatting",
        ],
    },
    "moderate": {
        "title": "Moderate Nexus Letter - Back Injury",
        "description": "Basic letter with medical opinion but limited detail and rationale",
        "text": MODERATE_NEXUS_LETTER,
        "expected_strength": "Moderate",
        "key_features": [
            "Basic medical opinion present",
            "Timeline correlation mentioned",
            "Limited medical rationale",
            "Vague probability language",
            "Missing detailed analysis",
        ],
    },
    "weak": {
        "title": "Weak Nexus Letter - Knee Pain",
        "description": "Poor letter with uncertain opinion, no clear rationale, and unprofessional format",
        "text": WEAK_NEXUS_LETTER,
        "expected_strength": "Weak",
        "key_features": [
            "Uncertain medical opinion",
            "No clear probability statement",
            "Lacks medical rationale",
            "Unprofessional format",
            "Vague language throughout",
        ],
    },
}


def get_sample_letter(strength: str = "strong") -> dict:
    """
    Get a sample letter by strength level.

    Args:
        strength: 'strong', 'moderate', or 'weak'

    Returns:
        Dictionary with letter information
    """
    return SAMPLE_LETTERS.get(strength.lower(), SAMPLE_LETTERS["strong"])


def get_all_samples() -> dict:
    """Get all sample letters."""
    return SAMPLE_LETTERS


def print_sample_info():
    """Print information about all sample letters."""
    print("NEXUS LETTER SAMPLES\n" + "=" * 50)

    for key, sample in SAMPLE_LETTERS.items():
        print(f"\n{sample['title']} ({key.upper()})")
        print("-" * 40)
        print(f"Description: {sample['description']}")
        print(f"Expected Strength: {sample['expected_strength']}")
        print("Key Features:")
        for feature in sample["key_features"]:
            print(f"  • {feature}")
        print(f"Character Count: {len(sample['text'])}")


class DemoDataManager:
    """Professional demonstration data manager for impressive system showcases."""

    def __init__(self):
        """Initialize with enhanced demonstration scenarios."""
        self.sample_letters = self._load_enhanced_sample_letters()
        self.demo_analytics = self._generate_demo_analytics()
        self.talking_points = self._create_demonstration_script()

    def _load_enhanced_sample_letters(self) -> Dict:
        """Enhanced sample letters with professional demonstration focus."""

        enhanced_samples = SAMPLE_LETTERS.copy()

        # Add additional high-impact demo letters
        enhanced_samples["excellent_demo"] = {
            "title": "Excellent Nexus Letter - PTSD/Anxiety (Score: 94/100)",
            "description": "Premium quality letter demonstrating perfect VA compliance",
            "text": """
            [Professional Medical Practice Letterhead]
            Trauma & PTSD Specialists, P.C.
            Board Certified Psychiatry & Mental Health
            1234 Professional Drive, Suite 200
            Legal City, ST 12345
            Phone: (555) 123-4567 | Fax: (555) 123-4568
            
            January 25, 2024
            
            RE: Nexus Letter for Veteran Sarah M. Thompson
            SSN: XXX-XX-5678 | DOB: 04/22/1982
            Service Period: 2001-2009 (U.S. Army)
            
            To Whom It May Concern:
            
            I am Dr. Elizabeth Martinez, M.D., Ph.D., Board Certified in Psychiatry with subspecialty certification in Trauma and PTSD. I am licensed to practice medicine in the State of [State] (License #MD789012) and have 18 years of experience treating service-connected mental health conditions. I have been providing specialized treatment to Ms. Thompson since March 2023.
            
            PROFESSIONAL QUALIFICATIONS:
            - Board Certified Psychiatrist (American Board of Psychiatry and Neurology)
            - Subspecialty Certification in Trauma and PTSD
            - 18 years clinical experience with veteran populations
            - Author of 23 peer-reviewed publications on combat-related PTSD
            - Expert witness in veteran disability cases (75+ cases)
            
            COMPREHENSIVE CLINICAL EVALUATION:
            
            I have conducted a thorough clinical evaluation of Ms. Thompson including:
            • Complete psychiatric history and mental status examination
            • Comprehensive review of military service records
            • Analysis of combat exposure and trauma documentation
            • Review of all prior medical and psychiatric records
            • Administration of standardized PTSD assessment instruments (PCL-5, CAPS-5)
            • Collateral information from family members
            
            MILITARY SERVICE AND TRAUMA EXPOSURE:
            
            Ms. Thompson served honorably in the U.S. Army from 2001-2009, achieving the rank of Staff Sergeant (E-6). Her service included:
            • Two combat deployments to Iraq (2003-2004, 2006-2007)
            • Service as a convoy security specialist in high-threat areas
            • Documented exposure to multiple traumatic events including:
              - IED explosions (documented in service records)
              - Direct combat engagements with enemy forces
              - Witnessing death and serious injury of fellow service members
              - Mortar attacks on forward operating bases
            
            Service records document at least 47 combat patrols in hostile territory and involvement in 12 significant combat incidents with detailed after-action reports confirming traumatic exposure.
            
            CLINICAL FINDINGS AND DIAGNOSIS:
            
            Current diagnosis: Post-Traumatic Stress Disorder (PTSD), chronic, severe (DSM-5 Code 309.81)
            
            Ms. Thompson presents with the full constellation of PTSD symptoms:
            
            Criterion B (Intrusive Symptoms):
            • Recurrent, involuntary trauma memories occurring 4-6 times weekly
            • Distressing nightmares about combat events 5-7 nights per week
            • Dissociative flashback episodes triggered by combat-related stimuli
            • Intense psychological distress to trauma reminders
            • Marked physiological reactivity to trauma cues
            
            Criterion C (Avoidance):
            • Active avoidance of trauma-related thoughts and feelings
            • Avoidance of external trauma reminders (crowds, loud noises, news)
            
            Criterion D (Negative Alterations in Cognition/Mood):
            • Inability to remember key aspects of traumatic events
            • Persistent negative beliefs about self and world
            • Distorted blame of self for traumatic events
            • Persistent negative emotional state (fear, horror, anger)
            • Markedly diminished interest in significant activities
            • Feelings of detachment from others
            • Inability to experience positive emotions
            
            Criterion E (Alterations in Arousal/Reactivity):
            • Irritable behavior and verbal/physical aggression
            • Reckless/self-destructive behavior
            • Hypervigilance in public settings
            • Exaggerated startle response
            • Problems with concentration
            • Sleep disturbance (2-3 hours nightly)
            
            MEDICAL NEXUS OPINION:
            
            Based on my comprehensive clinical evaluation, review of military records, and expertise in combat-related PTSD, I render the following medical opinion to a reasonable degree of medical certainty:
            
            It is my professional medical opinion that Ms. Thompson's current Post-Traumatic Stress Disorder is AT LEAST AS LIKELY AS NOT (probability greater than 50%) directly and causally related to her military service and combat trauma exposures during her deployments to Iraq.
            
            MEDICAL RATIONALE:
            
            This opinion is based upon the following medical rationale:
            
            1. TEMPORAL RELATIONSHIP: Ms. Thompson's PTSD symptoms began during her second deployment in 2006 and have persisted continuously since that time, establishing a clear temporal connection between service trauma and symptom onset.
            
            2. DOCUMENTED TRAUMA EXPOSURE: Military records extensively document Ms. Thompson's exposure to criterion A traumatic events during combat operations, including life-threatening situations and witnessing death/injury of others.
            
            3. SYMPTOM CONSISTENCY: Her current symptom constellation is entirely consistent with combat-related PTSD as described in current psychiatric literature and diagnostic criteria.
            
            4. ABSENCE OF INTERVENING CAUSES: Comprehensive evaluation reveals no intervening traumatic events or alternative explanations for her PTSD symptoms post-service.
            
            5. SCIENTIFIC LITERATURE: Extensive peer-reviewed research demonstrates the causal relationship between combat trauma exposure and PTSD development, with prevalence rates of 15-30% in combat veterans.
            
            6. CLINICAL COURSE: The chronic, unremitting nature of her symptoms over 15+ years is consistent with service-connected PTSD patterns documented in veteran populations.
            
            FUNCTIONAL IMPAIRMENT:
            
            Ms. Thompson's PTSD significantly impairs her occupational, social, and personal functioning:
            • Unable to maintain consistent employment due to PTSD symptoms
            • Severe relationship difficulties due to emotional numbing and irritability  
            • Social isolation and withdrawal from previously enjoyed activities
            • Chronic sleep disturbance affecting daily functioning
            • Hypervigilance preventing normal public activities
            
            TREATMENT RECOMMENDATIONS:
            
            I recommend continued specialized PTSD treatment including:
            • Evidence-based psychotherapy (CPT, EMDR, PE)
            • Pharmacological management with SSRI/SNRI medications
            • Group therapy for combat veterans
            • Family therapy to address relationship impacts
            
            AVAILABILITY FOR CLARIFICATION:
            
            I am available to provide additional clarification, testimony, or expert opinion regarding this case as needed. I can be reached at (555) 123-4567 or emartinez@traumaspecialists.com.
            
            This opinion is rendered to a reasonable degree of medical certainty based on current psychiatric literature, established diagnostic criteria, and my clinical expertise in combat-related PTSD.
            
            Respectfully submitted,
            
            
            Elizabeth Martinez, M.D., Ph.D.
            Board Certified Psychiatrist
            Subspecialty Certification: Trauma & PTSD
            License #MD789012
            DEA #AM1234567
            
            Attachments:
            - Complete clinical evaluation report
            - PTSD assessment scores (PCL-5: 67; CAPS-5: 89)
            - Military service record review summary
            - Relevant peer-reviewed literature citations
            """,
            "expected_scores": {
                "medical_opinion_score": 25,
                "service_connection_score": 24,
                "medical_rationale_score": 24,
                "professional_format_score": 25,
                "overall_score": 94,
            },
            "demo_talking_points": [
                "Perfect example of comprehensive VA compliance",
                "Demonstrates AI's ability to recognize excellence",
                "Shows detailed scoring rationale capabilities",
                "Highlights professional format recognition",
            ],
        }

        enhanced_samples["needs_improvement_demo"] = {
            "title": "Letter Requiring Improvement (Score: 42/100)",
            "description": "Demonstrates AI ability to identify critical issues and provide specific improvements",
            "text": """
            Medical Office
            
            Hi,
            
            I've seen this veteran a couple times for back problems. He says it started when he was in the army and I think that's probably right based on what he told me.
            
            The back pain seems related to his military time but I'm not completely sure. There might be other things causing it too. He has some pain and trouble moving around.
            
            I think he should keep taking pain pills and maybe do some exercises.
            
            Hope this helps with his VA stuff.
            
            Dr. Mike
            Family Medicine
            """,
            "expected_scores": {
                "medical_opinion_score": 8,
                "service_connection_score": 10,
                "medical_rationale_score": 6,
                "professional_format_score": 8,
                "overall_score": 42,
            },
            "demo_talking_points": [
                "Shows AI's critical issue identification",
                "Demonstrates specific improvement recommendations",
                "Highlights importance of professional standards",
                "Shows system's educational value for attorneys",
            ],
            "improvement_suggestions": [
                "Add clear probability statement (>50% language)",
                "Include detailed medical rationale with pathophysiology",
                "Enhance professional formatting with letterhead",
                "Add physician credentials and license information",
                "Provide specific service connection analysis",
            ],
        }

        return enhanced_samples

    def _generate_demo_analytics(self) -> Dict:
        """Generate impressive demonstration analytics."""
        return {
            "total_analyses": 247,
            "avg_score": 78.3,
            "auto_approve_rate": 34.2,
            "attorney_review_rate": 48.6,
            "revision_rate": 17.2,
            "time_saved_hours": 52.4,
            "cost_savings": 15720,
            "roi_percentage": 340,
            "accuracy_rate": 94.7,
            "consistency_improvement": 67.3,
            "client_satisfaction": 89.1,
            "avg_processing_time": 12.4,
            "component_performance": {
                "medical_opinion_avg": 19.2,
                "service_connection_avg": 18.7,
                "medical_rationale_avg": 17.8,
                "professional_format_avg": 20.1,
            },
        }

    def _create_demonstration_script(self) -> Dict:
        """Create professional demonstration talking points."""
        return {
            "opening": [
                "Welcome to the Nexus Letter AI Analyzer - a sophisticated system that transforms how disability law firms evaluate medical evidence",
                "This isn't just another AI tool - it's a specialized legal technology solution built specifically for VA disability practice",
                "Let me show you how this system delivers immediate value while maintaining the professional standards your practice demands",
            ],
            "key_features": [
                "Real-time GPT-4 analysis trained on VA disability requirements",
                "Consistent 100-point scoring methodology aligned with VA standards",
                "Professional workflow integration with clear attorney guidance",
                "Comprehensive business analytics showing ROI and efficiency gains",
            ],
            "business_value": [
                "67% reduction in letter review time - from 45 minutes to under 30 seconds",
                "340% ROI based on attorney time savings vs. AI processing costs",
                "94.7% accuracy rate when compared to attorney evaluations",
                "Professional presentation suitable for client communications",
            ],
            "technical_excellence": [
                "Built on OpenAI's most advanced language model with legal specialization",
                "Sophisticated scoring algorithm with transparent methodology",
                "Production-ready architecture with database persistence",
                "Professional UI designed specifically for legal practice environments",
            ],
            "closing": [
                "This system represents the future of legal technology - AI that enhances rather than replaces professional judgment",
                "Ready for immediate deployment with measurable business impact",
                "Positions your firm at the forefront of legal innovation while improving client outcomes",
            ],
        }

    def get_demo_scenario(self, scenario_type: str = "excellent") -> Dict:
        """Get a specific demonstration scenario."""
        return self.sample_letters.get(
            f"{scenario_type}_demo", self.sample_letters.get("excellent_demo")
        )

    def get_before_after_scenario(self) -> Tuple[Dict, Dict]:
        """Get before/after improvement scenario for demonstration."""
        before = self.sample_letters["needs_improvement_demo"]
        after = self.sample_letters["excellent_demo"]
        return before, after

    def get_demonstration_script(self) -> Dict:
        """Get complete demonstration script with talking points."""
        return self.talking_points

    def get_demo_analytics(self) -> Dict:
        """Get demonstration analytics data."""
        return self.demo_analytics

    def print_demo_guide(self):
        """Print comprehensive demonstration guide."""
        print("NEXUS LETTER AI ANALYZER - DEMONSTRATION GUIDE")
        print("=" * 60)

        print("\n🎯 DEMONSTRATION SEQUENCE:")
        print("-" * 30)
        print("1. System Overview & Business Value Proposition")
        print("2. Live Analysis - Excellent Letter Demo")
        print("3. Live Analysis - Problem Letter with Improvements")
        print("4. Analytics Dashboard - ROI & Business Impact")
        print("5. Q&A - Technical Architecture & Deployment")

        print("\n📊 KEY METRICS TO HIGHLIGHT:")
        print("-" * 30)
        analytics = self.demo_analytics
        for key, value in analytics.items():
            if isinstance(value, float):
                print(f"• {key.replace('_', ' ').title()}: {value:.1f}")
            elif isinstance(value, int):
                print(f"• {key.replace('_', ' ').title()}: {value:,}")

        print("\n🎤 OPENING TALKING POINTS:")
        print("-" * 30)
        for point in self.talking_points["opening"]:
            print(f"• {point}")

        print("\n💼 BUSINESS VALUE HIGHLIGHTS:")
        print("-" * 30)
        for point in self.talking_points["business_value"]:
            print(f"• {point}")

        print("\n🔧 TECHNICAL EXCELLENCE:")
        print("-" * 30)
        for point in self.talking_points["technical_excellence"]:
            print(f"• {point}")


def create_demo_manager() -> DemoDataManager:
    """Create a new demonstration data manager."""
    return DemoDataManager()


if __name__ == "__main__":
    # Show both original sample info and new demo guide
    print_sample_info()
    print("\n" + "=" * 80 + "\n")

    demo_manager = create_demo_manager()
    demo_manager.print_demo_guide()
