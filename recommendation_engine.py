"""Recommendation Engine for nexus letter improvement and workflow decisions."""

import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class WorkflowRecommendation:
    """Workflow decision and next steps."""

    decision: str  # 'auto_approve', 'attorney_review', 'revision_required'
    color: str  # 'green', 'yellow', 'red'
    icon: str  # Emoji icon for visual indicator
    message: str
    next_steps: List[str]
    confidence: float  # 0-1 confidence in recommendation


@dataclass
class ImprovementSuggestion:
    """Specific improvement suggestion."""

    component: str  # Which component needs improvement
    issue: str  # What's wrong
    suggestion: str  # How to fix it
    impact: str  # 'critical', 'high', 'medium', 'low'
    example: Optional[str] = None  # Example of improved text


class RecommendationEngine:
    """Generate actionable recommendations and workflow decisions for nexus letters."""

    # Score thresholds for workflow decisions
    AUTO_APPROVE_THRESHOLD = 85
    ATTORNEY_REVIEW_THRESHOLD = 70

    # Component-specific improvement templates
    IMPROVEMENT_TEMPLATES = {
        "medical_opinion": {
            "missing_probability": {
                "issue": "No VA-standard probability language found",
                "suggestion": 'Add clear probability statement using "at least as likely as not" or similar VA-approved language',
                "example": "It is at least as likely as not (50% or greater probability) that the veteran's condition is related to military service.",
                "impact": "critical",
            },
            "weak_probability": {
                "issue": "Weak or speculative probability language used",
                "suggestion": "Replace speculative terms with definitive VA-standard probability language",
                "example": 'Change "may be related" to "is at least as likely as not related"',
                "impact": "critical",
            },
            "no_clear_opinion": {
                "issue": "Medical opinion is unclear or equivocal",
                "suggestion": "Provide a clear, unambiguous medical opinion about the nexus",
                "impact": "critical",
            },
        },
        "service_connection": {
            "no_specific_events": {
                "issue": "No specific service events or exposures mentioned",
                "suggestion": "Include specific details about service events, deployments, or exposures",
                "example": "During deployment to Iraq in 2003-2004, the veteran was exposed to...",
                "impact": "high",
            },
            "unclear_linkage": {
                "issue": "Connection between service and condition is not explicit",
                "suggestion": "Clearly state how the service event caused or aggravated the condition",
                "impact": "high",
            },
            "missing_timeline": {
                "issue": "No temporal relationship established",
                "suggestion": "Include when symptoms began relative to service",
                "example": "Symptoms began during active duty service in...",
                "impact": "medium",
            },
        },
        "medical_rationale": {
            "no_explanation": {
                "issue": "No medical explanation for the connection",
                "suggestion": "Explain the medical/scientific basis for how service caused the condition",
                "impact": "high",
            },
            "no_literature": {
                "issue": "No medical literature or evidence cited",
                "suggestion": "Reference relevant medical studies or clinical guidelines",
                "example": "According to peer-reviewed medical literature...",
                "impact": "medium",
            },
            "weak_reasoning": {
                "issue": "Medical reasoning lacks logical chain",
                "suggestion": "Provide step-by-step explanation from cause to effect",
                "impact": "medium",
            },
        },
        "professional_format": {
            "missing_credentials": {
                "issue": "Physician credentials not clearly stated",
                "suggestion": "Include full name, degree, specialty, and license information",
                "example": "John Smith, MD, Board Certified in Internal Medicine, License #12345",
                "impact": "high",
            },
            "no_contact_info": {
                "issue": "Missing physician contact information",
                "suggestion": "Add complete contact information including address and phone",
                "impact": "medium",
            },
            "poor_structure": {
                "issue": "Letter lacks professional structure",
                "suggestion": "Use formal business letter format with clear sections",
                "impact": "low",
            },
        },
    }

    def __init__(self):
        """Initialize the recommendation engine."""
        logger.info("Recommendation engine initialized")

    def generate_recommendations(
        self, overall_score: int, component_scores: Dict, ai_analysis: Dict
    ) -> Dict:
        """
        Generate comprehensive recommendations based on analysis results.

        Args:
            overall_score: Total score (0-100)
            component_scores: Individual component score breakdowns
            ai_analysis: Complete AI analysis results

        Returns:
            Dictionary with workflow recommendation and improvement suggestions
        """
        try:
            # Generate workflow recommendation
            workflow_rec = self.generate_workflow_recommendation(overall_score)

            # Generate improvement suggestions
            improvements = self.generate_improvement_suggestions(
                component_scores, ai_analysis
            )

            # Prioritize improvements by impact
            prioritized_improvements = self.prioritize_improvements(improvements)

            # Generate client-suitable summary
            client_summary = self.generate_client_summary(
                overall_score, workflow_rec, prioritized_improvements
            )

            # Generate attorney notes if needed
            attorney_notes = None
            if workflow_rec.decision == "attorney_review":
                attorney_notes = self.generate_attorney_notes(
                    component_scores, prioritized_improvements
                )

            return {
                "workflow_recommendation": workflow_rec,
                "improvement_suggestions": prioritized_improvements,
                "client_summary": client_summary,
                "attorney_notes": attorney_notes,
                "total_improvements": len(improvements),
                "critical_issues": len(
                    [i for i in improvements if i.impact == "critical"]
                ),
            }

        except Exception as e:
            logger.error(f"Recommendation generation failed: {str(e)}")
            return self._create_error_recommendations(str(e))

    def generate_workflow_recommendation(
        self, overall_score: int
    ) -> WorkflowRecommendation:
        """
        Determine workflow pathway based on score.

        Args:
            overall_score: Total nexus letter score

        Returns:
            WorkflowRecommendation with decision and next steps
        """
        if overall_score >= self.AUTO_APPROVE_THRESHOLD:
            return WorkflowRecommendation(
                decision="auto_approve",
                color="green",
                icon="🟢",
                message="Letter meets VA standards - recommend proceeding with submission",
                next_steps=[
                    "Review for any final formatting edits",
                    "Prepare complete submission package",
                    "Submit to VA with confidence",
                ],
                confidence=0.95,
            )
        elif overall_score >= self.ATTORNEY_REVIEW_THRESHOLD:
            return WorkflowRecommendation(
                decision="attorney_review",
                color="yellow",
                icon="🟡",
                message="Letter requires attorney review before submission",
                next_steps=[
                    "Schedule attorney review within 24-48 hours",
                    "Address high-priority recommendations",
                    "Re-analyze after implementing attorney feedback",
                ],
                confidence=0.85,
            )
        else:
            return WorkflowRecommendation(
                decision="revision_required",
                color="red",
                icon="🔴",
                message="Letter needs significant revision before submission",
                next_steps=[
                    "Implement all critical recommendations immediately",
                    "Consider requesting new letter from physician",
                    "Schedule consultation to discuss revision strategy",
                    "Re-analyze after comprehensive revision",
                ],
                confidence=0.90,
            )

    def generate_improvement_suggestions(
        self, component_scores: Dict, ai_analysis: Dict
    ) -> List[ImprovementSuggestion]:
        """
        Generate specific improvement suggestions based on analysis.

        Args:
            component_scores: Component score breakdowns
            ai_analysis: AI analysis results

        Returns:
            List of improvement suggestions
        """
        suggestions = []

        # Check each component for improvement opportunities
        components = [
            "medical_opinion",
            "service_connection",
            "medical_rationale",
            "professional_format",
        ]

        for component in components:
            if component in ai_analysis:
                comp_analysis = ai_analysis[component]
                comp_score = component_scores.get(f"{component}_breakdown", {})

                # Get issues identified by AI
                issues = comp_analysis.get("issues", [])

                # Map issues to improvement templates
                suggestions.extend(
                    self._map_issues_to_suggestions(component, issues, comp_score)
                )

                # Check for low scores even without specific issues
                if hasattr(comp_score, "score") and comp_score.score < 15:
                    suggestions.extend(
                        self._generate_low_score_suggestions(component, comp_analysis)
                    )

        return suggestions

    def _map_issues_to_suggestions(
        self, component: str, issues: List[str], score_breakdown: any
    ) -> List[ImprovementSuggestion]:
        """Map identified issues to specific improvement suggestions."""
        suggestions = []
        templates = self.IMPROVEMENT_TEMPLATES.get(component, {})

        for issue in issues:
            issue_lower = issue.lower()

            # Match issues to templates
            for template_key, template in templates.items():
                if self._issue_matches_template(issue_lower, template_key):
                    suggestions.append(
                        ImprovementSuggestion(
                            component=component,
                            issue=issue,
                            suggestion=template["suggestion"],
                            impact=template["impact"],
                            example=template.get("example"),
                        )
                    )

        return suggestions

    def _issue_matches_template(self, issue_text: str, template_key: str) -> bool:
        """Check if an issue matches a template."""
        matching_patterns = {
            "missing_probability": [
                "no probability",
                "missing probability",
                "lacks probability",
            ],
            "weak_probability": [
                "weak",
                "speculative",
                "uncertain",
                "may be",
                "could be",
            ],
            "no_clear_opinion": ["unclear", "equivocal", "ambiguous"],
            "no_specific_events": ["no specific", "lacks detail", "vague"],
            "unclear_linkage": [
                "connection unclear",
                "linkage not",
                "relationship unclear",
            ],
            "missing_timeline": ["no timeline", "temporal", "when symptoms"],
            "no_explanation": ["no explanation", "lacks rationale", "missing basis"],
            "no_literature": ["no literature", "no references", "no studies"],
            "weak_reasoning": ["weak reasoning", "logic unclear", "chain missing"],
            "missing_credentials": [
                "credentials not",
                "no credentials",
                "physician info",
            ],
            "no_contact_info": ["no contact", "missing contact", "address missing"],
            "poor_structure": ["poor structure", "formatting", "organization"],
        }

        patterns = matching_patterns.get(template_key, [])
        return any(pattern in issue_text for pattern in patterns)

    def _generate_low_score_suggestions(
        self, component: str, comp_analysis: Dict
    ) -> List[ImprovementSuggestion]:
        """Generate suggestions for components with low scores."""
        suggestions = []

        # Generic low score suggestion
        suggestion = ImprovementSuggestion(
            component=component,
            issue=f'{component.replace("_", " ").title()} section needs significant improvement',
            suggestion=f'Comprehensively revise the {component.replace("_", " ")} section to meet VA standards',
            impact=(
                "high"
                if component in ["medical_opinion", "service_connection"]
                else "medium"
            ),
        )
        suggestions.append(suggestion)

        return suggestions

    def prioritize_improvements(
        self, improvements: List[ImprovementSuggestion]
    ) -> List[ImprovementSuggestion]:
        """
        Prioritize improvements by impact and component importance.

        Args:
            improvements: List of improvement suggestions

        Returns:
            Prioritized list of improvements
        """
        # Define priority weights
        impact_weights = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        component_weights = {
            "medical_opinion": 1.2,
            "service_connection": 1.1,
            "medical_rationale": 1.0,
            "professional_format": 0.9,
        }

        # Sort by weighted priority
        def priority_score(suggestion: ImprovementSuggestion) -> float:
            impact_score = impact_weights.get(suggestion.impact, 1)
            component_score = component_weights.get(suggestion.component, 1.0)
            return impact_score * component_score

        return sorted(improvements, key=priority_score, reverse=True)

    def generate_client_summary(
        self,
        overall_score: int,
        workflow_rec: WorkflowRecommendation,
        improvements: List[ImprovementSuggestion],
    ) -> str:
        """
        Generate a professional summary suitable for client communication.

        Args:
            overall_score: Total score
            workflow_rec: Workflow recommendation
            improvements: List of improvements

        Returns:
            Professional summary text
        """
        # Count improvements by impact
        critical_count = len([i for i in improvements if i.impact == "critical"])
        high_count = len([i for i in improvements if i.impact == "high"])

        summary = f"**Nexus Letter Analysis Summary**\n\n"
        summary += f"**Overall Assessment Score: {overall_score}/100**\n\n"
        summary += f"**Recommendation: {workflow_rec.message}**\n\n"

        if critical_count > 0:
            summary += f"⚠️ **Critical Issues Found:** {critical_count} issues must be addressed\n"
        if high_count > 0:
            summary += f"📋 **Important Improvements:** {high_count} high-priority improvements recommended\n"

        summary += f"\n**Next Steps:**\n"
        for i, step in enumerate(workflow_rec.next_steps[:3], 1):
            summary += f"{i}. {step}\n"

        if overall_score >= 85:
            summary += f"\n✅ This nexus letter demonstrates strong compliance with VA requirements."
        elif overall_score >= 70:
            summary += f"\n⚡ With the recommended improvements, this letter can meet VA standards."
        else:
            summary += f"\n🔧 Significant revisions are needed to meet VA requirements."

        return summary

    def generate_attorney_notes(
        self, component_scores: Dict, improvements: List[ImprovementSuggestion]
    ) -> str:
        """
        Generate detailed notes for attorney review.

        Args:
            component_scores: Component score breakdowns
            improvements: List of improvements

        Returns:
            Detailed attorney notes
        """
        notes = "**Attorney Review Notes**\n\n"
        notes += "**Component Score Analysis:**\n"

        # Add component scores
        for component in [
            "medical_opinion",
            "service_connection",
            "medical_rationale",
            "professional_format",
        ]:
            breakdown_key = f"{component}_breakdown"
            if breakdown_key in component_scores:
                score_info = component_scores[breakdown_key]
                if hasattr(score_info, "score"):
                    notes += f"- {component.replace('_', ' ').title()}: {score_info.score}/25\n"

        notes += "\n**Critical Review Points:**\n"

        # Group improvements by component
        by_component = {}
        for imp in improvements[:10]:  # Top 10 improvements
            if imp.component not in by_component:
                by_component[imp.component] = []
            by_component[imp.component].append(imp)

        for component, imps in by_component.items():
            notes += f"\n**{component.replace('_', ' ').title()}:**\n"
            for imp in imps:
                notes += f"- {imp.issue}\n"
                notes += f"  → {imp.suggestion}\n"
                if imp.example:
                    notes += f"  Example: {imp.example}\n"

        notes += "\n**Legal Considerations:**\n"
        notes += "- Review for compliance with 38 CFR § 3.303\n"
        notes += "- Ensure adherence to Hickson elements\n"
        notes += "- Verify McLendon criteria are addressed if applicable\n"

        return notes

    def _create_error_recommendations(self, error_message: str) -> Dict:
        """Create error recommendations when generation fails."""
        return {
            "workflow_recommendation": WorkflowRecommendation(
                decision="revision_required",
                color="red",
                icon="⚠️",
                message="Analysis error - manual review required",
                next_steps=["Retry analysis", "Contact support if issue persists"],
                confidence=0.0,
            ),
            "improvement_suggestions": [],
            "client_summary": f"Analysis encountered an error: {error_message}. Please retry.",
            "attorney_notes": None,
            "total_improvements": 0,
            "critical_issues": 0,
        }


def create_recommendation_engine() -> RecommendationEngine:
    """Create a new recommendation engine instance."""
    return RecommendationEngine()
