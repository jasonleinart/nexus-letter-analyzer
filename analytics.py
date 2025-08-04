"""Analytics engine for nexus letter analysis system metrics and insights."""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from database import AnalysisDatabase
import streamlit as st

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnalyticsEngine:
    """Calculate and manage analytics for the nexus letter analysis system."""
    
    def __init__(self, database: AnalysisDatabase):
        """
        Initialize analytics engine with database connection.
        
        Args:
            database: Database instance for data access
        """
        self.db = database
    
    def get_summary_metrics(self, days: int = 30) -> Dict:
        """
        Get summary metrics for the dashboard.
        
        Args:
            days: Number of days to include in metrics
            
        Returns:
            Dictionary of summary metrics
        """
        try:
            # Get raw analytics data
            analytics_data = self.db.get_analytics_data(days)
            overall = analytics_data.get('overall_metrics', {})
            
            # Calculate derived metrics
            total = overall.get('total_analyses', 0)
            auto_approve = overall.get('auto_approve_count', 0)
            attorney_review = overall.get('attorney_review_count', 0)
            revision_required = overall.get('revision_required_count', 0)
            
            # Calculate rates
            auto_approve_rate = (auto_approve / total * 100) if total > 0 else 0
            attorney_review_rate = (attorney_review / total * 100) if total > 0 else 0
            revision_rate = (revision_required / total * 100) if total > 0 else 0
            
            # Get week-over-week metrics
            week_metrics = self._get_week_over_week_metrics()
            
            return {
                'total_analyses': total,
                'analyses_this_week': week_metrics['current_week_count'],
                'avg_score': overall.get('avg_score', 0),
                'score_trend': week_metrics['score_trend'],
                'auto_approve_rate': auto_approve_rate,
                'attorney_review_rate': attorney_review_rate,
                'revision_rate': revision_rate,
                'approval_trend': week_metrics['approval_trend'],
                'avg_processing_time': overall.get('avg_processing_time', 0),
                'time_saved_hours': self._calculate_time_saved(total),
                'component_performance': analytics_data.get('component_performance', {})
            }
            
        except Exception as e:
            logger.error(f"Failed to get summary metrics: {str(e)}")
            return self._get_empty_metrics()
    
    def get_performance_trends(self, days: int = 30) -> Dict:
        """
        Get performance trend data for charting.
        
        Args:
            days: Number of days to include
            
        Returns:
            Dictionary with trend data
        """
        try:
            analytics_data = self.db.get_analytics_data(days)
            trend_data = analytics_data.get('trend_data', [])
            
            # Process trend data for charting
            dates = []
            counts = []
            scores = []
            
            for row in trend_data:
                dates.append(row['date'])
                counts.append(row['count'])
                scores.append(row['avg_score'])
            
            return {
                'dates': dates,
                'analysis_counts': counts,
                'average_scores': scores,
                'has_data': len(dates) > 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get performance trends: {str(e)}")
            return {'dates': [], 'analysis_counts': [], 'average_scores': [], 'has_data': False}
    
    def get_roi_metrics(self) -> Dict:
        """
        Calculate ROI metrics for business value demonstration.
        
        Returns:
            Dictionary of ROI metrics
        """
        try:
            # Get total analyses
            overall_data = self.db.get_analytics_data(90)  # 90 days for better ROI calc
            total = overall_data.get('overall_metrics', {}).get('total_analyses', 0)
            avg_time = overall_data.get('overall_metrics', {}).get('avg_processing_time', 30)
            
            # Business assumptions
            MANUAL_REVIEW_MINUTES = 45  # Time for manual review
            HOURLY_RATE = 150  # Attorney hourly rate
            AI_COST_PER_ANALYSIS = 0.50  # Estimated API cost
            
            # Calculate savings
            time_saved_minutes = total * (MANUAL_REVIEW_MINUTES - (avg_time / 60))
            time_saved_hours = time_saved_minutes / 60
            labor_cost_saved = time_saved_hours * HOURLY_RATE
            ai_costs = total * AI_COST_PER_ANALYSIS
            net_savings = labor_cost_saved - ai_costs
            
            # Calculate efficiency gain
            efficiency_gain = ((MANUAL_REVIEW_MINUTES * 60 - avg_time) / (MANUAL_REVIEW_MINUTES * 60)) * 100
            
            return {
                'total_analyses': total,
                'time_saved_hours': round(time_saved_hours, 1),
                'labor_cost_saved': round(labor_cost_saved, 2),
                'ai_costs': round(ai_costs, 2),
                'net_savings': round(net_savings, 2),
                'roi_percentage': round((net_savings / ai_costs * 100) if ai_costs > 0 else 0, 1),
                'efficiency_gain': round(efficiency_gain, 1),
                'avg_processing_seconds': round(avg_time, 1)
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate ROI metrics: {str(e)}")
            return self._get_empty_roi_metrics()
    
    def get_quality_metrics(self) -> Dict:
        """
        Get quality metrics for the analysis system.
        
        Returns:
            Dictionary of quality metrics
        """
        try:
            # Get recent analyses for quality assessment
            recent_analyses = self.db.get_recent_analyses(100)
            
            if not recent_analyses:
                return self._get_empty_quality_metrics()
            
            # Calculate quality indicators
            high_score_count = sum(1 for a in recent_analyses if a['overall_score'] >= 85)
            critical_issue_analyses = sum(1 for a in recent_analyses if a['critical_issues_count'] > 0)
            
            # Average metrics
            avg_score = sum(a['overall_score'] for a in recent_analyses) / len(recent_analyses)
            avg_processing_time = sum(a['processing_time_seconds'] for a in recent_analyses) / len(recent_analyses)
            
            # Score distribution
            score_distribution = {
                'excellent': sum(1 for a in recent_analyses if a['overall_score'] >= 85),
                'good': sum(1 for a in recent_analyses if 70 <= a['overall_score'] < 85),
                'fair': sum(1 for a in recent_analyses if 50 <= a['overall_score'] < 70),
                'poor': sum(1 for a in recent_analyses if a['overall_score'] < 50)
            }
            
            return {
                'total_analyzed': len(recent_analyses),
                'high_quality_rate': (high_score_count / len(recent_analyses) * 100),
                'critical_issue_rate': (critical_issue_analyses / len(recent_analyses) * 100),
                'average_score': avg_score,
                'average_processing_time': avg_processing_time,
                'score_distribution': score_distribution,
                'consistency_score': self._calculate_consistency_score(recent_analyses)
            }
            
        except Exception as e:
            logger.error(f"Failed to get quality metrics: {str(e)}")
            return self._get_empty_quality_metrics()
    
    # Helper methods
    def _get_week_over_week_metrics(self) -> Dict:
        """Calculate week-over-week comparison metrics."""
        try:
            # Get this week's data
            current_week_data = self.db.get_analytics_data(7)
            current_week = current_week_data.get('overall_metrics', {})
            
            # Get last week's data
            last_week_data = self.db.get_analytics_data(14)
            last_week_overall = last_week_data.get('overall_metrics', {})
            
            # Calculate last week metrics by subtracting current from 2-week total
            last_week_count = last_week_overall.get('total_analyses', 0) - current_week.get('total_analyses', 0)
            last_week_score = 0
            
            if last_week_count > 0 and current_week.get('total_analyses', 0) > 0:
                # Approximate last week's average score
                total_score_sum = last_week_overall.get('avg_score', 0) * last_week_overall.get('total_analyses', 0)
                current_score_sum = current_week.get('avg_score', 0) * current_week.get('total_analyses', 0)
                last_week_score = (total_score_sum - current_score_sum) / last_week_count if last_week_count > 0 else 0
            
            # Calculate trends
            score_trend = current_week.get('avg_score', 0) - last_week_score
            
            # Calculate approval trend
            current_approval_rate = 0
            last_approval_rate = 0
            
            if current_week.get('total_analyses', 0) > 0:
                current_approval_rate = (current_week.get('auto_approve_count', 0) / current_week.get('total_analyses', 0)) * 100
            
            if last_week_count > 0:
                last_auto_approve = last_week_overall.get('auto_approve_count', 0) - current_week.get('auto_approve_count', 0)
                last_approval_rate = (last_auto_approve / last_week_count) * 100
            
            approval_trend = current_approval_rate - last_approval_rate
            
            return {
                'current_week_count': current_week.get('total_analyses', 0),
                'last_week_count': last_week_count,
                'score_trend': score_trend,
                'approval_trend': approval_trend
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate week-over-week metrics: {str(e)}")
            return {
                'current_week_count': 0,
                'last_week_count': 0,
                'score_trend': 0,
                'approval_trend': 0
            }
    
    def _calculate_time_saved(self, total_analyses: int) -> float:
        """Calculate total time saved in hours."""
        # Assume manual review takes 45 minutes, AI takes 30 seconds
        MANUAL_MINUTES = 45
        AI_SECONDS = 30
        
        time_saved_minutes = total_analyses * (MANUAL_MINUTES - (AI_SECONDS / 60))
        return round(time_saved_minutes / 60, 1)
    
    def _calculate_consistency_score(self, analyses: List[Dict]) -> float:
        """Calculate consistency score based on score variance."""
        if len(analyses) < 2:
            return 100.0
        
        scores = [a['overall_score'] for a in analyses]
        avg_score = sum(scores) / len(scores)
        
        # Calculate variance
        variance = sum((score - avg_score) ** 2 for score in scores) / len(scores)
        std_dev = variance ** 0.5
        
        # Convert to consistency score (lower variance = higher consistency)
        # Max expected std dev of 20 points = 0% consistency
        consistency = max(0, 100 - (std_dev * 5))
        
        return round(consistency, 1)
    
    def _get_empty_metrics(self) -> Dict:
        """Return empty metrics structure."""
        return {
            'total_analyses': 0,
            'analyses_this_week': 0,
            'avg_score': 0,
            'score_trend': 0,
            'auto_approve_rate': 0,
            'attorney_review_rate': 0,
            'revision_rate': 0,
            'approval_trend': 0,
            'avg_processing_time': 0,
            'time_saved_hours': 0,
            'component_performance': {}
        }
    
    def _get_empty_roi_metrics(self) -> Dict:
        """Return empty ROI metrics structure."""
        return {
            'total_analyses': 0,
            'time_saved_hours': 0,
            'labor_cost_saved': 0,
            'ai_costs': 0,
            'net_savings': 0,
            'roi_percentage': 0,
            'efficiency_gain': 0,
            'avg_processing_seconds': 0
        }
    
    def _get_empty_quality_metrics(self) -> Dict:
        """Return empty quality metrics structure."""
        return {
            'total_analyzed': 0,
            'high_quality_rate': 0,
            'critical_issue_rate': 0,
            'average_score': 0,
            'average_processing_time': 0,
            'score_distribution': {
                'excellent': 0,
                'good': 0,
                'fair': 0,
                'poor': 0
            },
            'consistency_score': 0
        }


def display_analytics_dashboard(database: AnalysisDatabase):
    """
    Display the analytics dashboard in Streamlit.
    
    Args:
        database: Database instance for analytics
    """
    st.header("📈 System Analytics Dashboard")
    
    # Create analytics engine
    analytics = AnalyticsEngine(database)
    
    # Get metrics
    summary_metrics = analytics.get_summary_metrics()
    roi_metrics = analytics.get_roi_metrics()
    quality_metrics = analytics.get_quality_metrics()
    
    # Display key metrics in columns
    st.subheader("📊 Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Analyses",
            value=summary_metrics['total_analyses'],
            delta=f"{summary_metrics['analyses_this_week']} this week"
        )
    
    with col2:
        st.metric(
            label="Average Score",
            value=f"{summary_metrics['avg_score']:.1f}",
            delta=f"{summary_metrics['score_trend']:+.1f}"
        )
    
    with col3:
        st.metric(
            label="Auto-Approve Rate",
            value=f"{summary_metrics['auto_approve_rate']:.1f}%",
            delta=f"{summary_metrics['approval_trend']:+.1f}%"
        )
    
    with col4:
        st.metric(
            label="Avg Processing Time",
            value=f"{summary_metrics['avg_processing_time']:.1f}s"
        )
    
    st.divider()
    
    # ROI Section
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💰 Return on Investment")
        
        roi_col1, roi_col2 = st.columns(2)
        
        with roi_col1:
            st.metric("Time Saved", f"{roi_metrics['time_saved_hours']} hrs")
            st.metric("Net Savings", f"${roi_metrics['net_savings']:,.2f}")
        
        with roi_col2:
            st.metric("ROI", f"{roi_metrics['roi_percentage']}%")
            st.metric("Efficiency Gain", f"{roi_metrics['efficiency_gain']}%")
        
        # ROI breakdown
        with st.expander("View ROI Details"):
            st.markdown(f"""
            **Cost-Benefit Analysis (90 days):**
            - Labor Cost Saved: ${roi_metrics['labor_cost_saved']:,.2f}
            - AI Processing Costs: ${roi_metrics['ai_costs']:,.2f}
            - Net Savings: ${roi_metrics['net_savings']:,.2f}
            
            **Assumptions:**
            - Manual Review Time: 45 minutes
            - Attorney Hourly Rate: $150
            - AI Cost per Analysis: $0.50
            """)
    
    with col2:
        st.subheader("🎯 Quality Metrics")
        
        quality_col1, quality_col2 = st.columns(2)
        
        with quality_col1:
            st.metric("High Quality Rate", f"{quality_metrics['high_quality_rate']:.1f}%")
            st.metric("Consistency Score", f"{quality_metrics['consistency_score']:.1f}%")
        
        with quality_col2:
            st.metric("Critical Issue Rate", f"{quality_metrics['critical_issue_rate']:.1f}%")
            st.metric("Average Score", f"{quality_metrics['average_score']:.1f}")
        
        # Score distribution
        if quality_metrics['total_analyzed'] > 0:
            dist = quality_metrics['score_distribution']
            st.markdown("**Score Distribution:**")
            st.progress(dist['excellent'] / quality_metrics['total_analyzed'], 
                       text=f"Excellent (85+): {dist['excellent']}")
            st.progress(dist['good'] / quality_metrics['total_analyzed'],
                       text=f"Good (70-84): {dist['good']}")
            st.progress(dist['fair'] / quality_metrics['total_analyzed'],
                       text=f"Fair (50-69): {dist['fair']}")
            st.progress(dist['poor'] / quality_metrics['total_analyzed'],
                       text=f"Poor (<50): {dist['poor']}")
    
    st.divider()
    
    # Component Performance
    st.subheader("🔧 Component Performance Analysis")
    
    component_perf = summary_metrics.get('component_performance', {})
    if component_perf:
        comp_col1, comp_col2, comp_col3, comp_col4 = st.columns(4)
        
        with comp_col1:
            avg_medical = component_perf.get('avg_medical_opinion', 0) or 0
            st.metric("Medical Opinion", f"{avg_medical:.1f}/25")
            st.progress(avg_medical / 25)
        
        with comp_col2:
            avg_service = component_perf.get('avg_service_connection', 0) or 0
            st.metric("Service Connection", f"{avg_service:.1f}/25")
            st.progress(avg_service / 25)
        
        with comp_col3:
            avg_rationale = component_perf.get('avg_medical_rationale', 0) or 0
            st.metric("Medical Rationale", f"{avg_rationale:.1f}/25")
            st.progress(avg_rationale / 25)
        
        with comp_col4:
            avg_format = component_perf.get('avg_professional_format', 0) or 0
            st.metric("Professional Format", f"{avg_format:.1f}/25")
            st.progress(avg_format / 25)
    
    # Recent analyses
    st.divider()
    st.subheader("📋 Recent Analyses")
    
    recent = database.get_recent_analyses(5)
    if recent:
        for analysis in recent:
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                st.text(f"{analysis['letter_preview'][:60]}...")
            with col2:
                score_color = "🟢" if analysis['overall_score'] >= 85 else "🟡" if analysis['overall_score'] >= 70 else "🔴"
                st.text(f"{score_color} {analysis['overall_score']}/100")
            with col3:
                st.text(analysis['workflow_decision'].replace('_', ' ').title())
            with col4:
                st.text(f"{analysis['processing_time_seconds']:.1f}s")
    else:
        st.info("No analyses yet. Start analyzing nexus letters to see data here!")


def create_analytics_engine(database: AnalysisDatabase) -> AnalyticsEngine:
    """Create a new analytics engine instance."""
    return AnalyticsEngine(database)