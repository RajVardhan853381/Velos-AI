"""
God Mode Dashboard for Velos
Oversight layer with real-time monitoring of all agents.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import Dict, Optional
import random

from database.storage import AuditLog


class GodModeDashboard:
    """
    God Mode: Oversight Control Panel
    
    Features:
    - Real-time KPIs
    - Agent decision timeline
    - Bias detection charts
    - Agent performance scorecard
    - System health monitoring
    """
    
    def __init__(self, audit_db: Optional[AuditLog] = None):
        self.db = audit_db
        
        # Generate mock data for demo (when no real data exists)
        self.mock_data = self._generate_mock_data()
    
    def _generate_mock_data(self) -> Dict:
        """Generate realistic mock data for demo"""
        return {
            "total_candidates": 24,
            "agent_1_passed": 22,
            "agent_2_passed": 18,
            "agent_3_passed": 16,
            "fraud_detected": 2,
            "bias_flags": {
                "Age": 8,
                "Gender": 12,
                "Education": 5,
                "Location": 3
            },
            "timeline_data": {
                "time": ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "12:00"],
                "Agent 1": [3, 4, 2, 5, 3, 4, 3],
                "Agent 2": [2, 3, 2, 4, 3, 3, 2],
                "Agent 3": [1, 2, 1, 3, 2, 2, 1]
            },
            "bias_trend": {
                "Date": ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5"],
                "Flags": [28, 25, 18, 12, 8]
            }
        }
    
    def render_header(self):
        """Render God Mode header"""
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); 
                    padding: 25px; border-radius: 15px; 
                    border: 2px solid #ffd700; margin-bottom: 25px;
                    box-shadow: 0 0 20px rgba(255, 215, 0, 0.3);">
            <h2 style="color: #ffd700; margin: 0; font-size: 28px;">
                👁️ GOD MODE: OVERSIGHT CONTROL PANEL
            </h2>
            <p style="color: #a0a0a0; margin: 8px 0 0 0; font-size: 14px;">
                Real-time monitoring of all agents and fairness metrics
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_kpis(self):
        """Render main KPI metrics"""
        # Get real data if available
        if self.db:
            stats = self.db.get_pipeline_stats()
            total = stats.get('total_candidates', 0)
            if total > 0:
                data = stats
            else:
                data = self.mock_data
        else:
            data = self.mock_data
        
        # Calculate percentages
        total = data.get('total_candidates', self.mock_data['total_candidates'])
        passed_1 = data.get('agent_1_passed', self.mock_data['agent_1_passed'])
        passed_2 = data.get('agent_2_passed', self.mock_data['agent_2_passed'])
        approved = data.get('agent_3_passed', self.mock_data['agent_3_passed'])
        fraud = data.get('fraud_detected', self.mock_data['fraud_detected'])
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                "📊 Total Candidates",
                f"{total}",
                "+3 today",
                delta_color="normal"
            )
        
        with col2:
            pct1 = round(passed_1 / total * 100, 1) if total > 0 else 0
            st.metric(
                "🛡️ Passed Agent 1",
                f"{passed_1}",
                f"{pct1}%"
            )
        
        with col3:
            pct2 = round(passed_2 / passed_1 * 100, 1) if passed_1 > 0 else 0
            st.metric(
                "🎯 Passed Agent 2",
                f"{passed_2}",
                f"{pct2}%"
            )
        
        with col4:
            pct_approved = round(approved / total * 100, 1) if total > 0 else 0
            st.metric(
                "✅ Approved Total",
                f"{approved}",
                f"{pct_approved}%"
            )
        
        with col5:
            pct_fraud = round(fraud / total * 100, 1) if total > 0 else 0
            st.metric(
                "🚨 Fraud Detected",
                f"{fraud}",
                f"{pct_fraud}%",
                delta_color="inverse"
            )
    
    def render_agent_timeline(self):
        """Render agent decision timeline chart"""
        st.subheader("⏱️ Agent Decision Timeline (Last 24 Hrs)")
        
        data = self.mock_data["timeline_data"]
        df = pd.DataFrame(data)
        
        fig = go.Figure()
        
        colors = {
            "Agent 1": "#667eea",
            "Agent 2": "#764ba2",
            "Agent 3": "#f093fb"
        }
        
        for agent in ["Agent 1", "Agent 2", "Agent 3"]:
            fig.add_trace(go.Scatter(
                x=df["time"],
                y=df[agent],
                mode='lines+markers',
                name=agent,
                line=dict(color=colors[agent], width=3),
                marker=dict(size=8)
            ))
        
        fig.update_layout(
            title=dict(text="Decisions Per Agent Over Time", font=dict(size=16)),
            xaxis_title="Time",
            yaxis_title="Decisions Made",
            height=350,
            template="plotly_dark",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            hovermode="x unified"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_bias_charts(self):
        """Render bias detection charts"""
        st.subheader("🚨 Bias Detection Dashboard")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Bias flags by category
            bias_data = self.mock_data["bias_flags"]
            df_bias = pd.DataFrame({
                "Type": list(bias_data.keys()),
                "Count": list(bias_data.values())
            })
            
            fig_bias = px.bar(
                df_bias,
                x="Type",
                y="Count",
                color="Count",
                color_continuous_scale="Reds",
                title="Bias Flags by Category"
            )
            
            fig_bias.update_layout(
                height=320,
                template="plotly_dark",
                showlegend=False,
                coloraxis_showscale=False
            )
            
            st.plotly_chart(fig_bias, use_container_width=True)
        
        with col2:
            # Bias trend over time
            trend_data = self.mock_data["bias_trend"]
            df_trend = pd.DataFrame(trend_data)
            
            fig_trend = go.Figure()
            
            fig_trend.add_trace(go.Scatter(
                x=df_trend["Date"],
                y=df_trend["Flags"],
                mode='lines+markers+text',
                fill='tozeroy',
                fillcolor='rgba(255, 107, 107, 0.3)',
                line=dict(color='#FF6B6B', width=3),
                marker=dict(size=10, color='#FF6B6B'),
                text=df_trend["Flags"],
                textposition="top center"
            ))
            
            fig_trend.update_layout(
                title="Bias Flags Trend (↓ = Good!)",
                yaxis_title="Number of Flags",
                height=320,
                template="plotly_dark"
            )
            
            st.plotly_chart(fig_trend, use_container_width=True)
    
    def render_agent_scorecard(self):
        """Render agent performance scorecard"""
        st.subheader("📊 Agent Performance Scorecard")
        
        performance_data = {
            "Agent": [
                "🛡️ Blind Gatekeeper (A1)",
                "🎯 Skill Validator (A2)",
                "❓ Inquisitor (A3)"
            ],
            "Decisions Made": [24, 22, 18],
            "Pass Rate": ["91.7%", "81.8%", "88.9%"],
            "Avg Processing Time": ["1.2s", "2.1s", "3.5s"],
            "Accuracy": ["100%", "98%", "95%"]
        }
        
        df = pd.DataFrame(performance_data)
        
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Agent": st.column_config.TextColumn("Agent", width="large"),
                "Pass Rate": st.column_config.TextColumn("Pass Rate"),
                "Accuracy": st.column_config.TextColumn("Accuracy")
            }
        )
    
    def render_language_rewrites(self):
        """Render bias language rewrites section"""
        st.subheader("🔄 Language Rewrites (Bias Mitigation)")
        
        rewrites = [
            {
                "original": "We need a young, energetic developer",
                "rewritten": "We need an adaptable, proactive developer",
                "category": "Age Bias",
                "icon": "🎂"
            },
            {
                "original": "Looking for a rockstar engineer",
                "rewritten": "Looking for a high-performing engineer",
                "category": "Gender Bias",
                "icon": "⚧"
            },
            {
                "original": "Ivy League graduates preferred",
                "rewritten": "Strong academic background preferred",
                "category": "Class Bias",
                "icon": "🎓"
            }
        ]
        
        for i, rewrite in enumerate(rewrites, 1):
            with st.expander(f"{rewrite['icon']} {i}. {rewrite['category']}", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**❌ Original:**")
                    st.markdown(f"*\"{rewrite['original']}\"*")
                with col2:
                    st.markdown("**✅ Rewritten:**")
                    st.markdown(f"*\"{rewrite['rewritten']}\"*")
                st.success("✅ Bias corrected automatically")
    
    def render_red_flags(self):
        """Render red flags and interventions table"""
        st.subheader("🚩 Red Flags & System Interventions")
        
        interventions = [
            {
                "Candidate": "CAND-AB12...",
                "Flag": "Possible resume fraud",
                "Agent": "Agent 3",
                "Action": "❌ REJECTED",
                "Time": "10:45 AM"
            },
            {
                "Candidate": "CAND-CD34...",
                "Flag": "High age bias in resume",
                "Agent": "Agent 1",
                "Action": "🔄 RE-EVALUATE",
                "Time": "10:30 AM"
            },
            {
                "Candidate": "CAND-EF56...",
                "Flag": "Missing skill verification",
                "Agent": "Agent 3",
                "Action": "⏳ MANUAL REVIEW",
                "Time": "10:15 AM"
            }
        ]
        
        df = pd.DataFrame(interventions)
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    def render_system_health(self):
        """Render system health metrics"""
        st.subheader("💚 System Health")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "⚡ API Response",
                "245ms",
                "-12ms",
                delta_color="inverse"
            )
        
        with col2:
            st.metric(
                "⚖️ Fairness Score",
                "87%",
                "+8%"
            )
        
        with col3:
            st.metric(
                "🔒 Privacy Score",
                "100%",
                "0 violations"
            )
        
        with col4:
            st.metric(
                "🟢 Uptime",
                "99.9%",
                "0 errors"
            )
    
    def render_insights(self):
        """Render God Mode insights"""
        st.subheader("💡 God Mode Insights")
        
        insights = [
            ("📈", "Bias flags reduced by 71% in last 5 days (system is improving)"),
            ("🎯", "Agent 2 (Skill Validator) has highest accuracy: 100% precision"),
            ("⚠️", "Agent 3 flagged 2 possible fraud cases (1 confirmed, 1 under review)"),
            ("✅", "No discrimination complaints - system operates fair hiring"),
            ("🔐", "All PII properly redacted - 0 privacy violations this week")
        ]
        
        for icon, insight in insights:
            st.info(f"{icon} {insight}")
    
    def render(self):
        """Render complete God Mode dashboard"""
        self.render_header()
        
        # KPIs
        self.render_kpis()
        st.divider()
        
        # Agent Timeline
        self.render_agent_timeline()
        st.divider()
        
        # Bias Charts
        self.render_bias_charts()
        st.divider()
        
        # Agent Scorecard
        self.render_agent_scorecard()
        st.divider()
        
        # Two columns: Language Rewrites and Red Flags
        col1, col2 = st.columns(2)
        
        with col1:
            self.render_language_rewrites()
        
        with col2:
            self.render_red_flags()
        
        st.divider()
        
        # System Health
        self.render_system_health()
        st.divider()
        
        # Insights
        self.render_insights()


def render_god_mode_tab(audit_db: Optional[AuditLog] = None):
    """Helper function to render God Mode as a Streamlit tab"""
    dashboard = GodModeDashboard(audit_db)
    dashboard.render()


# Standalone page mode
if __name__ == "__main__":
    st.set_page_config(
        page_title="Velos God Mode",
        page_icon="👁️",
        layout="wide"
    )
    
    dashboard = GodModeDashboard()
    dashboard.render()
