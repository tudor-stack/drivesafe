"""
agent.py — DriveSafePipeline (root_agent)
SequentialAgent + LoopAgent pattern from adk-sql-agent presentation.
"""
from google.adk.agents import (
    LlmAgent,
    SequentialAgent,
    LoopAgent,
    ParallelAgent,
)

from .tools import (
    get_road_context_tool,
    compute_risk_score_tool,
    save_trip_to_firestore_tool,
    send_fcm_notification_tool,
)
from .prompts import (
    CONTEXT_AGENT_INSTRUCTION,
    BEHAVIOR_ANALYZER_INSTRUCTION,
    RISK_SCORER_INSTRUCTION,
    REFLEXION_AGENT_INSTRUCTION,
    COACH_AGENT_INSTRUCTION,
    TRIP_SUMMARY_AGENT_INSTRUCTION,
)

# Step 1: Context Agent
# Determines road context (road type, speed limit, traffic light)
context_agent = LlmAgent(
    name="context_agent",
    model="gemini-2.5-flash-lite",
    description="Determines road context for GPS coordinates of the event.",
    instruction=CONTEXT_AGENT_INSTRUCTION,
    tools=[get_road_context_tool],
)

# Step 2: RiskRefinementLoop
# Same pattern as RefinementLoop from the presentation (slide 18)
# BehaviorAnalyzer -> RiskScorer -> ReflexionAgent (GO/RETRY) — max 2 iterations

behavior_analyzer = LlmAgent(
    name="behavior_analyzer",
    model="gemini-2.5-flash-lite",
    description="Classifies dangerous driving behavior from sensor feature vectors.",
    instruction=BEHAVIOR_ANALYZER_INSTRUCTION,
)

risk_scorer = LlmAgent(
    name="risk_scorer",
    model="gemini-2.5-flash-lite",
    description="Calculates contextual risk score for detected behavior.",
    instruction=RISK_SCORER_INSTRUCTION,
    tools=[compute_risk_score_tool],
)

reflexion_agent = LlmAgent(
    name="reflexion_agent",
    model="gemini-2.5-flash-lite",
    description="Verifies risk score is contextually correct. Decides GO or RETRY.",
    instruction=REFLEXION_AGENT_INSTRUCTION,
)

risk_refinement_loop = LoopAgent(
    name="RiskRefinementLoop",
    sub_agents=[behavior_analyzer, risk_scorer, reflexion_agent],
    max_iterations=2,
)

# Step 3: OutputParallel
# TripSummaryAgent and CoachAgent run SIMULTANEOUSLY
# Saves ~2-3s compared to sequential execution

trip_summary_agent = LlmAgent(
    name="trip_summary_agent",
    model="gemini-2.5-flash-lite",
    description="Aggregates processed events into final document and saves to Firestore.",
    instruction=TRIP_SUMMARY_AGENT_INSTRUCTION,
    tools=[save_trip_to_firestore_tool, send_fcm_notification_tool],
)

coach_agent = LlmAgent(
    name="coach_agent",
    model="gemini-2.5-flash-lite",
    description="Generates personalized coaching report for the beginner driver.",
    instruction=COACH_AGENT_INSTRUCTION,
)

output_parallel = ParallelAgent(
    name="OutputParallel",
    sub_agents=[trip_summary_agent, coach_agent],
)

# Root Agent: DriveSafePipeline
# Same structure as SecureSQLPipeline from presentation (slide 18)
root_agent = SequentialAgent(
    name="DriveSafePipeline",
    sub_agents=[
        context_agent,
        risk_refinement_loop,
        output_parallel,
    ],
    description=(
        "Complete post-trip analysis pipeline: "
        "road context -> risk scoring with reflexion -> coach report + Firestore save."
    ),
)
