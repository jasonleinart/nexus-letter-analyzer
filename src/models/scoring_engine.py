"""VA Compliance Scoring Engine for nexus letter analysis."""

import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ScoreBreakdown:
    """Detailed breakdown of a component score."""

    score: int
    max_score: int
    criteria: Dict[str, int]
    rationale: str


class VAComplianceScorer:
    """Transparent, consistent scoring algorithm based on VA nexus letter requirements."""

    # VA-standard probability phrases
    VA_PROBABILITY_PHRASES = [
        "at least as likely as not",
        "more likely than not",
        "as likely as not",
        "50 percent or greater",
        "50% or greater",
        ">50%",
        "greater than 50",
        "more than 50 percent",
    ]

    # Weak probability indicators
    WEAK_PROBABILITY_PHRASES = [
        "possible",
        "may be",
        "could be",
        "might be",
        "potentially",
        "perhaps",
    ]

    def __init__(self):
        """Initialize the scoring engine."""
        self.component_weights = {
            "medical_opinion": 25,
            "service_connection": 25,
            "medical_rationale": 25,
            "professional_format": 25,
        }

    def calculate_total_score(self, ai_analysis: Dict) -> Dict:
        """
        Calculate the total score and detailed breakdown from AI analysis.

        Args:
            ai_analysis: AI analysis results with component evaluations

        Returns:
            Complete scoring results with breakdowns
        """
        try:
            # Calculate individual component scores
            medical_opinion_result = self.calculate_medical_opinion_score(
                ai_analysis.get("medical_opinion", {})
            )
            service_connection_result = self.calculate_service_connection_score(
                ai_analysis.get("service_connection", {})
            )
            medical_rationale_result = self.calculate_medical_rationale_score(
                ai_analysis.get("medical_rationale", {})
            )
            professional_format_result = self.calculate_professional_format_score(
                ai_analysis.get("professional_format", {})
            )

            # Calculate total score
            total_score = (
                medical_opinion_result.score
                + service_connection_result.score
                + medical_rationale_result.score
                + professional_format_result.score
            )

            # Validate total score bounds
            total_score = max(0, min(100, total_score))

            return {
                "overall_score": total_score,
                "medical_opinion_breakdown": medical_opinion_result,
                "service_connection_breakdown": service_connection_result,
                "medical_rationale_breakdown": medical_rationale_result,
                "professional_format_breakdown": professional_format_result,
                "score_summary": self._generate_score_summary(total_score),
            }

        except Exception as e:
            logger.error(f"Score calculation failed: {str(e)}")
            return self._create_error_score_result(str(e))

    def calculate_medical_opinion_score(
        self, component_analysis: Dict
    ) -> ScoreBreakdown:
        """
        Score the medical opinion component based on VA criteria.

        Args:
            component_analysis: AI analysis of medical opinion component

        Returns:
            ScoreBreakdown with detailed scoring
        """
        criteria_scores = {
            "probability_language": 0,
            "opinion_certainty": 0,
            "medical_basis": 0,
        }

        # Extract findings and issues
        findings = component_analysis.get("findings", [])
        issues = component_analysis.get("issues", [])
        ai_score = component_analysis.get("score", 0)

        # Probability language (10 points max)
        if self._has_va_probability_language(findings):
            criteria_scores["probability_language"] = 10
        elif self._has_weak_probability_language(findings, issues):
            criteria_scores["probability_language"] = 3
        else:
            criteria_scores["probability_language"] = 0

        # Opinion certainty (10 points max)
        if self._has_definitive_opinion(findings, issues):
            criteria_scores["opinion_certainty"] = 10
        elif len(issues) > 0 and any(
            "equivocal" in issue.lower() or "unclear" in issue.lower()
            for issue in issues
        ):
            criteria_scores["opinion_certainty"] = 5
        else:
            criteria_scores["opinion_certainty"] = 7

        # Medical basis (5 points max)
        if any("medical" in finding.lower() for finding in findings):
            criteria_scores["medical_basis"] = 5
        else:
            criteria_scores["medical_basis"] = 2

        total_score = sum(criteria_scores.values())

        # Apply confidence adjustment
        confidence = component_analysis.get("confidence", 100)
        if confidence < 70:
            total_score = int(total_score * 0.9)

        # Ensure score doesn't exceed maximum
        total_score = min(total_score, 25)

        return ScoreBreakdown(
            score=total_score,
            max_score=25,
            criteria=criteria_scores,
            rationale=self._generate_component_rationale(
                "medical_opinion", criteria_scores, findings, issues
            ),
        )

    def calculate_service_connection_score(
        self, component_analysis: Dict
    ) -> ScoreBreakdown:
        """
        Score the service connection component based on VA criteria.

        Args:
            component_analysis: AI analysis of service connection component

        Returns:
            ScoreBreakdown with detailed scoring
        """
        criteria_scores = {
            "explicit_linkage": 0,
            "specific_events": 0,
            "temporal_clarity": 0,
        }

        findings = component_analysis.get("findings", [])
        issues = component_analysis.get("issues", [])

        # Explicit linkage (10 points max)
        if any(
            "service" in finding.lower() and "condition" in finding.lower()
            for finding in findings
        ):
            criteria_scores["explicit_linkage"] = 10
        elif len(findings) > 0:
            criteria_scores["explicit_linkage"] = 5

        # Specific service events (10 points max)
        if self._has_specific_service_events(findings):
            criteria_scores["specific_events"] = 10
        elif any("service" in finding.lower() for finding in findings):
            criteria_scores["specific_events"] = 5

        # Temporal clarity (5 points max)
        if self._has_temporal_relationship(findings):
            criteria_scores["temporal_clarity"] = 5
        elif any(
            "during" in finding.lower() or "after" in finding.lower()
            for finding in findings
        ):
            criteria_scores["temporal_clarity"] = 3

        total_score = sum(criteria_scores.values())

        # Apply confidence adjustment
        confidence = component_analysis.get("confidence", 100)
        if confidence < 70:
            total_score = int(total_score * 0.9)

        total_score = min(total_score, 25)

        return ScoreBreakdown(
            score=total_score,
            max_score=25,
            criteria=criteria_scores,
            rationale=self._generate_component_rationale(
                "service_connection", criteria_scores, findings, issues
            ),
        )

    def calculate_medical_rationale_score(
        self, component_analysis: Dict
    ) -> ScoreBreakdown:
        """
        Score the medical rationale component based on VA criteria.

        Args:
            component_analysis: AI analysis of medical rationale component

        Returns:
            ScoreBreakdown with detailed scoring
        """
        criteria_scores = {
            "clinical_explanation": 0,
            "literature_support": 0,
            "logical_reasoning": 0,
        }

        findings = component_analysis.get("findings", [])
        issues = component_analysis.get("issues", [])

        # Clinical explanation (10 points max)
        if self._has_clinical_explanation(findings):
            criteria_scores["clinical_explanation"] = 10
        elif any(
            "medical" in finding.lower() or "clinical" in finding.lower()
            for finding in findings
        ):
            criteria_scores["clinical_explanation"] = 6
        else:
            criteria_scores["clinical_explanation"] = 3

        # Literature support (8 points max)
        if self._has_literature_references(findings):
            criteria_scores["literature_support"] = 8
        elif any(
            "research" in finding.lower() or "study" in finding.lower()
            for finding in findings
        ):
            criteria_scores["literature_support"] = 4

        # Logical reasoning (7 points max)
        if self._has_logical_chain(findings):
            criteria_scores["logical_reasoning"] = 7
        elif len(findings) > 1:
            criteria_scores["logical_reasoning"] = 4
        else:
            criteria_scores["logical_reasoning"] = 2

        total_score = sum(criteria_scores.values())

        # Apply confidence adjustment
        confidence = component_analysis.get("confidence", 100)
        if confidence < 70:
            total_score = int(total_score * 0.9)

        total_score = min(total_score, 25)

        return ScoreBreakdown(
            score=total_score,
            max_score=25,
            criteria=criteria_scores,
            rationale=self._generate_component_rationale(
                "medical_rationale", criteria_scores, findings, issues
            ),
        )

    def calculate_professional_format_score(
        self, component_analysis: Dict
    ) -> ScoreBreakdown:
        """
        Score the professional format component based on VA criteria.

        Args:
            component_analysis: AI analysis of professional format component

        Returns:
            ScoreBreakdown with detailed scoring
        """
        criteria_scores = {
            "credentials_stated": 0,
            "contact_info": 0,
            "proper_structure": 0,
            "medical_terminology": 0,
        }

        findings = component_analysis.get("findings", [])
        issues = component_analysis.get("issues", [])

        # Credentials stated (8 points max)
        if self._has_physician_credentials(findings):
            criteria_scores["credentials_stated"] = 8
        elif any(
            "dr" in finding.lower() or "physician" in finding.lower()
            for finding in findings
        ):
            criteria_scores["credentials_stated"] = 4

        # Contact information (6 points max)
        if self._has_contact_info(findings):
            criteria_scores["contact_info"] = 6
        elif any(
            "address" in finding.lower() or "phone" in finding.lower()
            for finding in findings
        ):
            criteria_scores["contact_info"] = 3

        # Proper structure (6 points max)
        if len(findings) > 2 and not any(
            "poor structure" in issue.lower() for issue in issues
        ):
            criteria_scores["proper_structure"] = 6
        else:
            criteria_scores["proper_structure"] = 3

        # Medical terminology (5 points max)
        if self._has_proper_medical_terminology(findings):
            criteria_scores["medical_terminology"] = 5
        else:
            criteria_scores["medical_terminology"] = 2

        total_score = sum(criteria_scores.values())

        # Apply confidence adjustment
        confidence = component_analysis.get("confidence", 100)
        if confidence < 70:
            total_score = int(total_score * 0.9)

        total_score = min(total_score, 25)

        return ScoreBreakdown(
            score=total_score,
            max_score=25,
            criteria=criteria_scores,
            rationale=self._generate_component_rationale(
                "professional_format", criteria_scores, findings, issues
            ),
        )

    # Helper methods for criteria evaluation
    def _has_va_probability_language(self, findings: List[str]) -> bool:
        """Check if VA-standard probability language is present."""
        findings_text = " ".join(findings).lower()
        return any(phrase in findings_text for phrase in self.VA_PROBABILITY_PHRASES)

    def _has_weak_probability_language(
        self, findings: List[str], issues: List[str]
    ) -> bool:
        """Check if weak probability language is present."""
        all_text = " ".join(findings + issues).lower()
        return any(phrase in all_text for phrase in self.WEAK_PROBABILITY_PHRASES)

    def _has_definitive_opinion(self, findings: List[str], issues: List[str]) -> bool:
        """Check if the opinion is definitive vs speculative."""
        positive_indicators = ["clear", "definitive", "certain", "conclusive"]
        negative_indicators = ["speculative", "uncertain", "equivocal", "unclear"]

        findings_text = " ".join(findings).lower()
        issues_text = " ".join(issues).lower()

        has_positive = any(
            indicator in findings_text for indicator in positive_indicators
        )
        has_negative = any(
            indicator in issues_text for indicator in negative_indicators
        )

        return has_positive and not has_negative

    def _has_specific_service_events(self, findings: List[str]) -> bool:
        """Check for specific service events or exposures."""
        event_indicators = [
            "deployment",
            "combat",
            "exposure",
            "incident",
            "injury",
            "event",
        ]
        findings_text = " ".join(findings).lower()
        return any(indicator in findings_text for indicator in event_indicators)

    def _has_temporal_relationship(self, findings: List[str]) -> bool:
        """Check for temporal relationship clarity."""
        temporal_indicators = [
            "during service",
            "in service",
            "while serving",
            "onset",
            "began",
            "started",
        ]
        findings_text = " ".join(findings).lower()
        return any(indicator in findings_text for indicator in temporal_indicators)

    def _has_clinical_explanation(self, findings: List[str]) -> bool:
        """Check for clinical/scientific explanation."""
        clinical_indicators = [
            "pathophysiology",
            "mechanism",
            "etiology",
            "clinical",
            "medical basis",
        ]
        findings_text = " ".join(findings).lower()
        return any(indicator in findings_text for indicator in clinical_indicators)

    def _has_literature_references(self, findings: List[str]) -> bool:
        """Check for medical literature references."""
        literature_indicators = [
            "literature",
            "research",
            "study",
            "journal",
            "evidence",
            "published",
        ]
        findings_text = " ".join(findings).lower()
        return any(indicator in findings_text for indicator in literature_indicators)

    def _has_logical_chain(self, findings: List[str]) -> bool:
        """Check for logical reasoning chain."""
        logic_indicators = [
            "therefore",
            "because",
            "due to",
            "result of",
            "caused by",
            "leading to",
        ]
        findings_text = " ".join(findings).lower()
        return any(indicator in findings_text for indicator in logic_indicators)

    def _has_physician_credentials(self, findings: List[str]) -> bool:
        """Check for physician credentials."""
        credential_indicators = [
            "md",
            "m.d.",
            "do",
            "d.o.",
            "physician",
            "doctor",
            "licensed",
        ]
        findings_text = " ".join(findings).lower()
        return any(indicator in findings_text for indicator in credential_indicators)

    def _has_contact_info(self, findings: List[str]) -> bool:
        """Check for contact information."""
        contact_indicators = ["address", "phone", "fax", "email", "contact"]
        findings_text = " ".join(findings).lower()
        return any(indicator in findings_text for indicator in contact_indicators)

    def _has_proper_medical_terminology(self, findings: List[str]) -> bool:
        """Check for proper medical terminology usage."""
        medical_terms = [
            "diagnosis",
            "condition",
            "symptom",
            "treatment",
            "prognosis",
            "etiology",
        ]
        findings_text = " ".join(findings).lower()
        return sum(1 for term in medical_terms if term in findings_text) >= 2

    def _generate_component_rationale(
        self,
        component: str,
        criteria_scores: Dict[str, int],
        findings: List[str],
        issues: List[str],
    ) -> str:
        """Generate rationale for component scoring."""
        total_points = sum(criteria_scores.values())
        max_points = 25

        rationale = f"{component.replace('_', ' ').title()} scored {total_points}/{max_points} points. "

        # Add criteria-specific feedback
        high_scoring = [k for k, v in criteria_scores.items() if v >= 7]
        low_scoring = [k for k, v in criteria_scores.items() if v < 5]

        if high_scoring:
            rationale += f"Strong elements: {', '.join(high_scoring)}. "
        if low_scoring:
            rationale += f"Areas for improvement: {', '.join(low_scoring)}. "

        # Add issue count if present
        if issues:
            rationale += f"Found {len(issues)} issues to address."

        return rationale

    def _generate_score_summary(self, total_score: int) -> str:
        """Generate summary based on total score."""
        if total_score >= 85:
            return "Excellent nexus letter that strongly meets VA standards. Minor improvements may enhance it further."
        elif total_score >= 70:
            return "Good nexus letter that meets most VA requirements. Some improvements recommended before submission."
        elif total_score >= 50:
            return "Adequate nexus letter with significant gaps. Substantial improvements needed for optimal results."
        else:
            return "Nexus letter has major deficiencies. Comprehensive revision strongly recommended."

    def _create_error_score_result(self, error_message: str) -> Dict:
        """Create error result when scoring fails."""
        return {
            "overall_score": 0,
            "error": True,
            "error_message": error_message,
            "medical_opinion_breakdown": ScoreBreakdown(0, 25, {}, "Error in scoring"),
            "service_connection_breakdown": ScoreBreakdown(
                0, 25, {}, "Error in scoring"
            ),
            "medical_rationale_breakdown": ScoreBreakdown(
                0, 25, {}, "Error in scoring"
            ),
            "professional_format_breakdown": ScoreBreakdown(
                0, 25, {}, "Error in scoring"
            ),
            "score_summary": "Scoring failed due to error. Please retry analysis.",
        }


def create_scorer() -> VAComplianceScorer:
    """Create a new scorer instance."""
    return VAComplianceScorer()
