"""SQLite database integration for nexus letter analysis storage and tracking."""

import sqlite3
import json
import logging
import hashlib
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from contextlib import contextmanager
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnalysisDatabase:
    """SQLite database for storing nexus letter analyses and metrics."""

    def __init__(self, db_path: str = "nexus_analyses.db"):
        """
        Initialize database connection and ensure schema exists.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.connection = None
        self._initialize_database()

    def _initialize_database(self):
        """Initialize database with schema if it doesn't exist."""
        try:
            with self._get_connection() as conn:
                self._create_tables(conn)
                self._migrate_schema(conn)
                logger.info(f"Database initialized at {self.db_path}")
        except Exception as e:
            logger.error(f"Database initialization failed: {str(e)}")
            raise

    @contextmanager
    def _get_connection(self):
        """Context manager for database connections."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            yield conn
        finally:
            if conn:
                conn.close()

    def _create_tables(self, conn: sqlite3.Connection):
        """Create database tables if they don't exist."""

        # Main analyses table
        analyses_table = """
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            letter_hash TEXT NOT NULL UNIQUE,
            letter_preview TEXT NOT NULL,
            overall_score INTEGER NOT NULL,
            overall_recommendation TEXT NOT NULL,
            workflow_decision TEXT NOT NULL,
            medical_opinion_score INTEGER NOT NULL,
            service_connection_score INTEGER NOT NULL,
            medical_rationale_score INTEGER NOT NULL,
            professional_format_score INTEGER NOT NULL,
            ai_response_json TEXT NOT NULL,
            scoring_details_json TEXT NOT NULL,
            recommendations_json TEXT NOT NULL,
            processing_time_seconds REAL NOT NULL,
            nexus_strength TEXT,
            primary_condition TEXT,
            critical_issues_count INTEGER DEFAULT 0,
            improvement_count INTEGER DEFAULT 0,
            patient_name TEXT,
            patient_anonymized TEXT,
            doctor_name TEXT,
            facility_name TEXT
        )"""

        # Component scores table for detailed tracking
        component_scores_table = """
        CREATE TABLE IF NOT EXISTS component_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id INTEGER NOT NULL,
            component_name TEXT NOT NULL,
            score INTEGER NOT NULL,
            max_score INTEGER NOT NULL,
            confidence INTEGER,
            criteria_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE
        )"""

        # Improvement suggestions table
        improvements_table = """
        CREATE TABLE IF NOT EXISTS improvement_suggestions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id INTEGER NOT NULL,
            component TEXT NOT NULL,
            issue TEXT NOT NULL,
            suggestion TEXT NOT NULL,
            impact TEXT NOT NULL,
            example TEXT,
            implemented BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE
        )"""

        # Analytics summary table
        analytics_summary_table = """
        CREATE TABLE IF NOT EXISTS analytics_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL UNIQUE,
            total_analyses INTEGER DEFAULT 0,
            avg_score REAL DEFAULT 0,
            auto_approve_count INTEGER DEFAULT 0,
            attorney_review_count INTEGER DEFAULT 0,
            revision_required_count INTEGER DEFAULT 0,
            avg_processing_time REAL DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )"""

        # Create indices for performance
        indices = [
            "CREATE INDEX IF NOT EXISTS idx_analyses_created_at ON analyses(created_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_analyses_letter_hash ON analyses(letter_hash)",
            "CREATE INDEX IF NOT EXISTS idx_analyses_workflow ON analyses(workflow_decision)",
            "CREATE INDEX IF NOT EXISTS idx_component_scores_analysis ON component_scores(analysis_id)",
            "CREATE INDEX IF NOT EXISTS idx_improvements_analysis ON improvement_suggestions(analysis_id)",
            "CREATE INDEX IF NOT EXISTS idx_analytics_date ON analytics_summary(date)",
        ]

        # Execute table creation
        cursor = conn.cursor()
        cursor.execute(analyses_table)
        cursor.execute(component_scores_table)
        cursor.execute(improvements_table)
        cursor.execute(analytics_summary_table)

        # Create indices
        for index in indices:
            cursor.execute(index)

        conn.commit()

    def _migrate_schema(self, conn: sqlite3.Connection):
        """Migrate database schema for existing installations."""
        cursor = conn.cursor()

        # Check if new columns exist
        columns = cursor.execute("PRAGMA table_info(analyses)").fetchall()
        existing_columns = [col[1] for col in columns]

        # Add new metadata columns if they don't exist
        new_columns = [
            "patient_name TEXT",
            "patient_anonymized TEXT",
            "doctor_name TEXT",
            "facility_name TEXT",
        ]

        for col_def in new_columns:
            col_name = col_def.split()[0]
            if col_name not in existing_columns:
                try:
                    cursor.execute(f"ALTER TABLE analyses ADD COLUMN {col_def}")
                    logger.info(f"Added column {col_name} to analyses table")
                except Exception as e:
                    logger.warning(f"Could not add column {col_name}: {str(e)}")

        conn.commit()

    def _extract_metadata(self, letter_text: str) -> tuple:
        """Extract patient, doctor, and facility information from letter text."""
        import re

        patient_name = None
        doctor_name = None
        facility_name = None

        try:
            # Extract patient name - multiple patterns
            patient_patterns = [
                # Standard nexus letter format
                r"RE:.*?for\s+([A-Za-z\s\.]+?)(?:\n|DOB|SSN|\s*$)",
                # Alternative format "on behalf of [Name]"
                r"on behalf of\s+([A-Za-z\s\.]+?)(?:\s*\(|DOB|$)",
                # Mr./Ms. format
                r"(?:Mr\.|Ms\.|Mrs\.)\s+([A-Za-z\s\.]+?)(?:\s|$|\()",
            ]

            for pattern in patient_patterns:
                re_match = re.search(pattern, letter_text, re.IGNORECASE)
                if re_match:
                    extracted = re_match.group(1).strip()
                    # Clean up common artifacts
                    extracted = re.sub(r"\s*\.\.\.$", "", extracted)
                    extracted = re.sub(r"\s+", " ", extracted)
                    if len(extracted) > 2 and not extracted.lower() in [
                        "patient",
                        "veteran",
                        "individual",
                    ]:
                        patient_name = extracted
                        break

            # Extract doctor name - enhanced patterns
            doctor_patterns = [
                # [Dr. Name] format
                r"\[Dr\.\s+([A-Za-z\s\.]+?)\]",
                # Dr. Name, M.D. format
                r"Dr\.\s+([A-Za-z\s\.]+?)(?:,\s*M\.D\.|$|\n)",
                # Name, M.D. format
                r"([A-Za-z\s\.]+?),?\s+M\.D\.",
                # Sincerely format
                r"Sincerely,\s*([A-Za-z\s\.]+?)(?:\n|M\.D\.|$)",
                # I am Dr. format
                r"I am Dr\.\s+([A-Za-z\s\.]+?)(?:,|\n|$)",
            ]

            for pattern in doctor_patterns:
                doc_match = re.search(
                    pattern, letter_text, re.MULTILINE | re.IGNORECASE
                )
                if doc_match:
                    extracted = doc_match.group(1).strip()
                    # Clean up artifacts
                    extracted = re.sub(r"\s*\.\.\.$", "", extracted)
                    extracted = re.sub(r"\s+", " ", extracted)
                    if len(extracted) > 2:
                        # If pattern didn't include Dr., add it back for consistency
                        if not extracted.startswith(("Dr.", "Doctor")):
                            extracted = f"Dr. {extracted}"
                        doctor_name = extracted
                        break

            # Extract facility - improved patterns
            lines = letter_text.split("\n")
            for line in lines[:5]:  # Check first 5 lines
                line = line.strip()
                # Skip lines that are clearly not facility names
                if (
                    line
                    and "Department" not in line
                    and "Phone" not in line
                    and "Email" not in line
                    and "Date:" not in line
                    and not line.startswith("[")
                    and len(line) > 5
                ):

                    # Look for medical facility indicators
                    if any(
                        word in line.lower()
                        for word in ["medical", "center", "hospital", "clinic", "plaza"]
                    ):
                        facility_name = line
                        break
                    # If no medical keywords, check if it looks like a facility name
                    elif len(line) > 10 and not any(char in line for char in "()[]@"):
                        facility_name = line
                        break

        except Exception as e:
            logger.warning(f"Error extracting metadata: {str(e)}")

        return patient_name, doctor_name, facility_name

    def _anonymize_name(self, name: str) -> str:
        """Convert patient name to initials for privacy protection."""
        if not name:
            return None

        try:
            parts = name.strip().split()
            if len(parts) >= 2:
                # First name initial + Last name initial
                return f"{parts[0][0]}. {parts[-1][0]}."
            else:
                return f"{name[0]}." if name else None
        except:
            return None

    def save_analysis(
        self,
        letter_text: str,
        ai_analysis: Dict,
        scoring_results: Dict,
        recommendations: Dict,
        processing_time: float,
    ) -> Dict:
        """
        Save a complete analysis to the database.

        Args:
            letter_text: Original letter text
            ai_analysis: AI analysis results
            scoring_results: Scoring engine results
            recommendations: Recommendation engine results
            processing_time: Time taken to process

        Returns:
            Dictionary with analysis_id and metadata
        """
        try:
            # Generate letter hash for duplicate detection
            letter_hash = self._generate_letter_hash(letter_text)

            # Create letter preview (first 200 chars)
            letter_preview = (
                letter_text[:200] + "..." if len(letter_text) > 200 else letter_text
            )

            # Extract metadata once during save
            patient_name, doctor_name, facility_name = self._extract_metadata(
                letter_text
            )
            patient_anonymized = (
                self._anonymize_name(patient_name) if patient_name else None
            )

            # Extract key fields
            overall_score = scoring_results.get("overall_score", 0)
            workflow_rec = recommendations.get("workflow_recommendation", {})
            workflow_decision = (
                workflow_rec.decision
                if hasattr(workflow_rec, "decision")
                else "unknown"
            )

            # Extract component scores
            medical_opinion_score = self._extract_component_score(
                scoring_results, "medical_opinion"
            )
            service_connection_score = self._extract_component_score(
                scoring_results, "service_connection"
            )
            medical_rationale_score = self._extract_component_score(
                scoring_results, "medical_rationale"
            )
            professional_format_score = self._extract_component_score(
                scoring_results, "professional_format"
            )

            # Count issues and improvements
            improvements = recommendations.get("improvement_suggestions", [])
            critical_issues = recommendations.get("critical_issues", 0)

            # Prepare JSON fields
            ai_response_json = json.dumps(ai_analysis)
            scoring_details_json = json.dumps(
                self._serialize_scoring_results(scoring_results)
            )
            recommendations_json = json.dumps(
                self._serialize_recommendations(recommendations)
            )

            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Check if analysis already exists
                existing = cursor.execute(
                    "SELECT id FROM analyses WHERE letter_hash = ?", (letter_hash,)
                ).fetchone()

                if existing:
                    logger.info(
                        f"Analysis already exists for this letter (ID: {existing['id']})"
                    )
                    return {
                        "analysis_id": existing["id"],
                        "metadata": {
                            "patient_name": patient_name,
                            "patient_anonymized": patient_anonymized,
                            "doctor_name": doctor_name,
                            "facility_name": facility_name,
                        },
                    }

                # Insert new analysis
                cursor.execute(
                    """
                    INSERT INTO analyses (
                        letter_hash, letter_preview, overall_score, overall_recommendation,
                        workflow_decision, medical_opinion_score, service_connection_score,
                        medical_rationale_score, professional_format_score,
                        ai_response_json, scoring_details_json, recommendations_json,
                        processing_time_seconds, nexus_strength, primary_condition,
                        critical_issues_count, improvement_count,
                        patient_name, patient_anonymized, doctor_name, facility_name
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        letter_hash,
                        letter_preview,
                        overall_score,
                        (
                            workflow_rec.message
                            if hasattr(workflow_rec, "message")
                            else ""
                        ),
                        workflow_decision,
                        medical_opinion_score,
                        service_connection_score,
                        medical_rationale_score,
                        professional_format_score,
                        ai_response_json,
                        scoring_details_json,
                        recommendations_json,
                        processing_time,
                        ai_analysis.get("nexus_strength", "Unknown"),
                        ai_analysis.get("primary_condition", "Unknown"),
                        critical_issues,
                        len(improvements),
                        patient_name,
                        patient_anonymized,
                        doctor_name,
                        facility_name,
                    ),
                )

                analysis_id = cursor.lastrowid

                # Save component scores
                self._save_component_scores(conn, analysis_id, scoring_results)

                # Save improvement suggestions
                self._save_improvements(conn, analysis_id, improvements)

                # Update analytics summary
                self._update_analytics_summary(conn)

                conn.commit()
                logger.info(f"Analysis saved successfully (ID: {analysis_id})")

                return {
                    "analysis_id": analysis_id,
                    "metadata": {
                        "patient_name": patient_name,
                        "patient_anonymized": patient_anonymized,
                        "doctor_name": doctor_name,
                        "facility_name": facility_name,
                    },
                }

        except Exception as e:
            logger.error(f"Failed to save analysis: {str(e)}")
            raise

    def get_analysis(self, analysis_id: int) -> Optional[Dict]:
        """
        Retrieve a complete analysis by ID.

        Args:
            analysis_id: Analysis ID

        Returns:
            Complete analysis data or None
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Get main analysis
                analysis = cursor.execute(
                    "SELECT * FROM analyses WHERE id = ?", (analysis_id,)
                ).fetchone()

                if not analysis:
                    return None

                # Convert to dictionary
                result = dict(analysis)

                # Parse JSON fields
                result["ai_response"] = json.loads(result.pop("ai_response_json"))
                result["scoring_details"] = json.loads(
                    result.pop("scoring_details_json")
                )
                result["recommendations"] = json.loads(
                    result.pop("recommendations_json")
                )

                # Get component scores
                result["component_scores"] = self._get_component_scores(
                    conn, analysis_id
                )

                # Get improvement suggestions
                result["improvements"] = self._get_improvements(conn, analysis_id)

                return result

        except Exception as e:
            logger.error(f"Failed to retrieve analysis: {str(e)}")
            return None

    def get_recent_analyses(self, limit: int = 10) -> List[Dict]:
        """
        Get recent analyses for display.

        Args:
            limit: Maximum number of analyses to return

        Returns:
            List of recent analysis summaries
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                analyses = cursor.execute(
                    """
                    SELECT id, created_at, letter_preview, overall_score,
                           workflow_decision, primary_condition, 
                           critical_issues_count, processing_time_seconds
                    FROM analyses
                    ORDER BY created_at DESC
                    LIMIT ?
                """,
                    (limit,),
                ).fetchall()

                return [dict(analysis) for analysis in analyses]

        except Exception as e:
            logger.error(f"Failed to retrieve recent analyses: {str(e)}")
            return []

    def get_analytics_data(self, days: int = 30) -> Dict:
        """
        Get analytics data for dashboard.

        Args:
            days: Number of days to include

        Returns:
            Analytics data dictionary
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Get overall metrics
                overall_metrics = cursor.execute(
                    """
                    SELECT 
                        COUNT(*) as total_analyses,
                        AVG(overall_score) as avg_score,
                        AVG(processing_time_seconds) as avg_processing_time,
                        SUM(CASE WHEN workflow_decision = 'auto_approve' THEN 1 ELSE 0 END) as auto_approve_count,
                        SUM(CASE WHEN workflow_decision = 'attorney_review' THEN 1 ELSE 0 END) as attorney_review_count,
                        SUM(CASE WHEN workflow_decision = 'revision_required' THEN 1 ELSE 0 END) as revision_required_count
                    FROM analyses
                    WHERE created_at >= datetime('now', '-' || ? || ' days')
                """,
                    (days,),
                ).fetchone()

                # Get trend data
                trend_data = cursor.execute(
                    """
                    SELECT 
                        DATE(created_at) as date,
                        COUNT(*) as count,
                        AVG(overall_score) as avg_score
                    FROM analyses
                    WHERE created_at >= datetime('now', '-' || ? || ' days')
                    GROUP BY DATE(created_at)
                    ORDER BY date
                """,
                    (days,),
                ).fetchall()

                # Get component performance
                component_performance = cursor.execute(
                    """
                    SELECT 
                        AVG(medical_opinion_score) as avg_medical_opinion,
                        AVG(service_connection_score) as avg_service_connection,
                        AVG(medical_rationale_score) as avg_medical_rationale,
                        AVG(professional_format_score) as avg_professional_format
                    FROM analyses
                    WHERE created_at >= datetime('now', '-' || ? || ' days')
                """,
                    (days,),
                ).fetchone()

                return {
                    "overall_metrics": dict(overall_metrics) if overall_metrics else {},
                    "trend_data": [dict(row) for row in trend_data],
                    "component_performance": (
                        dict(component_performance) if component_performance else {}
                    ),
                }

        except Exception as e:
            logger.error(f"Failed to retrieve analytics data: {str(e)}")
            return {}

    # Helper methods
    def _generate_letter_hash(self, letter_text: str) -> str:
        """Generate hash for letter deduplication."""
        # Normalize text (remove extra whitespace, lowercase)
        normalized = " ".join(letter_text.lower().split())
        return hashlib.sha256(normalized.encode()).hexdigest()

    def _extract_component_score(self, scoring_results: Dict, component: str) -> int:
        """Extract component score from scoring results."""
        breakdown_key = f"{component}_breakdown"
        if breakdown_key in scoring_results:
            breakdown = scoring_results[breakdown_key]
            if hasattr(breakdown, "score"):
                return breakdown.score
        return 0

    def _serialize_scoring_results(self, scoring_results: Dict) -> Dict:
        """Serialize scoring results for JSON storage."""
        serialized = scoring_results.copy()

        # Handle ScoreBreakdown objects
        for key, value in scoring_results.items():
            if hasattr(value, "__dict__"):
                # Convert ScoreBreakdown objects to dictionaries
                serialized[key] = {
                    "score": getattr(value, "score", 0),
                    "max_score": getattr(value, "max_score", 25),
                    "criteria": getattr(value, "criteria", {}),
                    "rationale": getattr(value, "rationale", ""),
                }

        return serialized

    def _serialize_recommendations(self, recommendations: Dict) -> Dict:
        """Serialize recommendations for JSON storage."""
        serialized = recommendations.copy()

        # Handle WorkflowRecommendation object
        if "workflow_recommendation" in serialized:
            rec = serialized["workflow_recommendation"]
            if hasattr(rec, "__dict__"):
                serialized["workflow_recommendation"] = rec.__dict__

        # Handle ImprovementSuggestion objects
        if "improvement_suggestions" in serialized:
            suggestions = []
            for imp in serialized["improvement_suggestions"]:
                if hasattr(imp, "__dict__"):
                    suggestions.append(imp.__dict__)
                else:
                    suggestions.append(imp)
            serialized["improvement_suggestions"] = suggestions

        return serialized

    def _save_component_scores(
        self, conn: sqlite3.Connection, analysis_id: int, scoring_results: Dict
    ):
        """Save individual component scores."""
        cursor = conn.cursor()

        components = [
            "medical_opinion",
            "service_connection",
            "medical_rationale",
            "professional_format",
        ]

        for component in components:
            breakdown_key = f"{component}_breakdown"
            if breakdown_key in scoring_results:
                breakdown = scoring_results[breakdown_key]
                if hasattr(breakdown, "score"):
                    cursor.execute(
                        """
                        INSERT INTO component_scores 
                        (analysis_id, component_name, score, max_score, criteria_json)
                        VALUES (?, ?, ?, ?, ?)
                    """,
                        (
                            analysis_id,
                            component,
                            breakdown.score,
                            breakdown.max_score,
                            (
                                json.dumps(breakdown.criteria)
                                if hasattr(breakdown, "criteria")
                                else "{}"
                            ),
                        ),
                    )

    def _save_improvements(
        self, conn: sqlite3.Connection, analysis_id: int, improvements: List
    ):
        """Save improvement suggestions."""
        cursor = conn.cursor()

        for imp in improvements:
            if hasattr(imp, "__dict__"):
                imp_dict = imp.__dict__
            else:
                imp_dict = imp

            cursor.execute(
                """
                INSERT INTO improvement_suggestions 
                (analysis_id, component, issue, suggestion, impact, example)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    analysis_id,
                    imp_dict.get("component", ""),
                    imp_dict.get("issue", ""),
                    imp_dict.get("suggestion", ""),
                    imp_dict.get("impact", ""),
                    imp_dict.get("example", ""),
                ),
            )

    def _update_analytics_summary(self, conn: sqlite3.Connection):
        """Update daily analytics summary."""
        cursor = conn.cursor()
        today = datetime.now().date()

        # Calculate today's metrics
        metrics = cursor.execute(
            """
            SELECT 
                COUNT(*) as total,
                AVG(overall_score) as avg_score,
                SUM(CASE WHEN workflow_decision = 'auto_approve' THEN 1 ELSE 0 END) as auto_approve,
                SUM(CASE WHEN workflow_decision = 'attorney_review' THEN 1 ELSE 0 END) as attorney_review,
                SUM(CASE WHEN workflow_decision = 'revision_required' THEN 1 ELSE 0 END) as revision_required,
                AVG(processing_time_seconds) as avg_time
            FROM analyses
            WHERE DATE(created_at) = ?
        """,
            (today,),
        ).fetchone()

        # Update or insert summary
        cursor.execute(
            """
            INSERT OR REPLACE INTO analytics_summary 
            (date, total_analyses, avg_score, auto_approve_count, 
             attorney_review_count, revision_required_count, avg_processing_time)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                today,
                metrics["total"],
                metrics["avg_score"],
                metrics["auto_approve"],
                metrics["attorney_review"],
                metrics["revision_required"],
                metrics["avg_time"],
            ),
        )

    def _get_component_scores(
        self, conn: sqlite3.Connection, analysis_id: int
    ) -> List[Dict]:
        """Get component scores for an analysis."""
        cursor = conn.cursor()
        scores = cursor.execute(
            """
            SELECT * FROM component_scores 
            WHERE analysis_id = ?
            ORDER BY component_name
        """,
            (analysis_id,),
        ).fetchall()

        return [dict(score) for score in scores]

    def _get_improvements(
        self, conn: sqlite3.Connection, analysis_id: int
    ) -> List[Dict]:
        """Get improvement suggestions for an analysis."""
        cursor = conn.cursor()
        improvements = cursor.execute(
            """
            SELECT * FROM improvement_suggestions 
            WHERE analysis_id = ?
            ORDER BY impact DESC, component
        """,
            (analysis_id,),
        ).fetchall()

        return [dict(imp) for imp in improvements]

    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")


def create_database(db_path: str = "nexus_analyses.db") -> AnalysisDatabase:
    """Create a new database instance."""
    return AnalysisDatabase(db_path)
