"""Sample nexus letters for testing and demonstration."""

# Sample nexus letters with varying strengths for testing

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
    'strong': {
        'title': 'Strong Nexus Letter - Coronary Artery Disease',
        'description': 'Well-structured letter with clear medical opinion, detailed rationale, and proper probability language',
        'text': STRONG_NEXUS_LETTER,
        'expected_strength': 'Strong',
        'key_features': [
            'Clear probability statement (>50%)',
            'Detailed medical rationale',
            'Service connection well-established',
            'Board-certified physician',
            'Literature references',
            'Professional formatting'
        ]
    },
    'moderate': {
        'title': 'Moderate Nexus Letter - Back Injury',
        'description': 'Basic letter with medical opinion but limited detail and rationale',
        'text': MODERATE_NEXUS_LETTER,
        'expected_strength': 'Moderate',
        'key_features': [
            'Basic medical opinion present',
            'Timeline correlation mentioned',
            'Limited medical rationale',
            'Vague probability language',
            'Missing detailed analysis'
        ]
    },
    'weak': {
        'title': 'Weak Nexus Letter - Knee Pain',
        'description': 'Poor letter with uncertain opinion, no clear rationale, and unprofessional format',
        'text': WEAK_NEXUS_LETTER,
        'expected_strength': 'Weak',
        'key_features': [
            'Uncertain medical opinion',
            'No clear probability statement',
            'Lacks medical rationale',
            'Unprofessional format',
            'Vague language throughout'
        ]
    }
}

def get_sample_letter(strength: str = 'strong') -> dict:
    """
    Get a sample letter by strength level.
    
    Args:
        strength: 'strong', 'moderate', or 'weak'
        
    Returns:
        Dictionary with letter information
    """
    return SAMPLE_LETTERS.get(strength.lower(), SAMPLE_LETTERS['strong'])

def get_all_samples() -> dict:
    """Get all sample letters."""
    return SAMPLE_LETTERS

def print_sample_info():
    """Print information about all sample letters."""
    print("NEXUS LETTER SAMPLES\n" + "="*50)
    
    for key, sample in SAMPLE_LETTERS.items():
        print(f"\n{sample['title']} ({key.upper()})")
        print("-" * 40)
        print(f"Description: {sample['description']}")
        print(f"Expected Strength: {sample['expected_strength']}")
        print("Key Features:")
        for feature in sample['key_features']:
            print(f"  • {feature}")
        print(f"Character Count: {len(sample['text'])}")

if __name__ == "__main__":
    print_sample_info()