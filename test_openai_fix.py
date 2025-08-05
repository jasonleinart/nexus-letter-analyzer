"""Test script to verify OpenAI API is working after fix."""

from ai_analyzer import create_analyzer


def test_openai_connection():
    """Test the OpenAI API connection after fixing the proxies error."""
    print("🔍 Testing OpenAI API Connection...")
    print("-" * 50)

    try:
        # Create analyzer instance
        analyzer = create_analyzer()
        print("✅ Analyzer created successfully")

        # Test connection
        success, message = analyzer.test_connection()
        if success:
            print(f"✅ API Connection Test: {message}")
        else:
            print(f"❌ API Connection Test Failed: {message}")
            return False

        # Test actual analysis
        test_letter = """
        Medical Center
        123 Main St
        
        RE: Nexus Letter for John Doe
        
        To Whom It May Concern,
        
        I am Dr. Smith, treating Mr. Doe for PTSD. In my medical opinion, 
        it is at least as likely as not (50% or greater probability) that 
        his PTSD is directly related to his military service.
        
        Sincerely,
        Dr. Smith, M.D.
        """

        print("\n📝 Testing letter analysis...")
        result = analyzer.analyze_letter(test_letter)

        if not result.get("error"):
            print("✅ Analysis completed successfully!")
            print(f"   - Nexus Strength: {result['analysis']['nexus_strength']}")
            print(
                f"   - Medical Opinion Present: {result['analysis']['medical_opinion_present']}"
            )
            return True
        else:
            print(f"❌ Analysis failed: {result.get('message')}")
            return False

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


if __name__ == "__main__":
    test_openai_connection()
