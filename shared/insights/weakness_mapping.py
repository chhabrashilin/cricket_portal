"""
Weakness category to drill mapping.

This module defines the complete mapping of weakness categories to
specific drills and focus points. This is the "coaching knowledge base"
that translates detected weaknesses into actionable training recommendations.
"""
from typing import Dict, List
from shared.types.enums import WeaknessCategory

# Weakness category → Drills mapping
WEAKNESS_DRILLS: Dict[WeaknessCategory, List[str]] = {
    WeaknessCategory.SHORT_BALL_PULL: [
        "Short ball pull-shot practice (20 minutes)",
        "Chest-height pull shot drills with bowling machine",
        "Back-foot pull shot technique work",
        "Judging bounce and getting into position early",
        "Head position during pull shots"
    ],
    WeaknessCategory.FULL_BALL_DRIVE: [
        "Full-length driving practice (20 minutes)",
        "Forward defense to drive transition drills",
        "Getting to the pitch of the ball",
        "Balance and weight transfer on full deliveries",
        "Straight drive technique refinement"
    ],
    WeaknessCategory.GOOD_LENGTH_DEFENSE: [
        "Good length defense practice (15 minutes)",
        "Compact defense technique",
        "Head position over the ball",
        "Soft hands and bat angle",
        "Playing close to the body"
    ],
    WeaknessCategory.WIDE_OUTSIDE_OFF: [
        "Wide delivery practice (15 minutes)",
        "Cut shot technique on wide deliveries",
        "Judging which wide deliveries to play",
        "Balance when reaching for wide balls",
        "Avoiding chasing wide deliveries"
    ],
    WeaknessCategory.SPINNING_BALL_FOTWORK: [
        "Footwork vs spin practice (20 minutes)",
        "Getting forward to spinners",
        "Reading spin and adjusting footwork",
        "Sweep shot technique",
        "Using feet to get to the pitch"
    ],
    WeaknessCategory.BACKLIFT_ANGLE_INCONSISTENT: [
        "Backlift consistency drills (15 minutes)",
        "Shadow batting with focus on backlift",
        "Maintaining consistent backlift angle",
        "Backlift position for different shot types",
        "Getting bat into position early"
    ],
    WeaknessCategory.LATE_CONTACT_POINT: [
        "Timing practice (20 minutes)",
        "Playing late and close to the body",
        "Watching the ball closely",
        "Judging length early",
        "Contact point drills with varied pace"
    ],
    WeaknessCategory.HEAD_STABILITY: [
        "Head position drills (15 minutes)",
        "Keeping head still during shot",
        "Head over the ball",
        "Head position for different deliveries",
        "Balance and head stability exercises"
    ],
    WeaknessCategory.FOOTWORK_STABILITY: [
        "Footwork drills (20 minutes)",
        "Front foot movement practice",
        "Back foot stability",
        "Foot spacing and positioning",
        "Weight transfer drills"
    ],
    WeaknessCategory.TIMING_CONSISTENCY: [
        "Timing and rhythm practice (20 minutes)",
        "Consistent swing speed",
        "Playing with the pace of the ball",
        "Timing drills with varied deliveries",
        "Rhythm and tempo work"
    ],
}

# Weakness category → Focus points mapping
WEAKNESS_FOCUS_POINTS: Dict[WeaknessCategory, List[str]] = {
    WeaknessCategory.SHORT_BALL_PULL: [
        "Judge bounce early",
        "Get into position quickly",
        "Keep head still",
        "Transfer weight to back foot",
        "Watch the ball onto the bat"
    ],
    WeaknessCategory.FULL_BALL_DRIVE: [
        "Get forward to the pitch",
        "Head over the ball",
        "Straight bat path",
        "Complete follow-through",
        "Balance throughout the shot"
    ],
    WeaknessCategory.GOOD_LENGTH_DEFENSE: [
        "Play close to the body",
        "Soft hands",
        "Head over the ball",
        "Compact technique",
        "Watch the ball closely"
    ],
    WeaknessCategory.WIDE_OUTSIDE_OFF: [
        "Judge which deliveries to play",
        "Avoid chasing wide balls",
        "Maintain balance",
        "Use cut shot technique",
        "Keep head still"
    ],
    WeaknessCategory.SPINNING_BALL_FOTWORK: [
        "Use feet to get to the pitch",
        "Read spin early",
        "Get forward to spinners",
        "Adjust footwork for different spin",
        "Balance when using feet"
    ],
    WeaknessCategory.BACKLIFT_ANGLE_INCONSISTENT: [
        "Maintain consistent backlift",
        "Get bat into position early",
        "Backlift angle for shot type",
        "Smooth backlift motion",
        "Avoid excessive backlift"
    ],
    WeaknessCategory.LATE_CONTACT_POINT: [
        "Play late and close to body",
        "Watch the ball closely",
        "Judge length early",
        "Time the ball",
        "Contact point for different deliveries"
    ],
    WeaknessCategory.HEAD_STABILITY: [
        "Keep head still",
        "Head over the ball",
        "Avoid head movement",
        "Balance and head position",
        "Head position for shot type"
    ],
    WeaknessCategory.FOOTWORK_STABILITY: [
        "Front foot movement",
        "Back foot stability",
        "Proper foot spacing",
        "Weight transfer",
        "Foot position for shot type"
    ],
    WeaknessCategory.TIMING_CONSISTENCY: [
        "Consistent swing speed",
        "Time the ball",
        "Play with the pace",
        "Rhythm and tempo",
        "Contact point timing"
    ],
}

# Weakness category descriptions
WEAKNESS_DESCRIPTIONS: Dict[WeaknessCategory, str] = {
    WeaknessCategory.SHORT_BALL_PULL: "Struggles with pull shots to short-pitched deliveries",
    WeaknessCategory.FULL_BALL_DRIVE: "Issues with driving full-length deliveries",
    WeaknessCategory.GOOD_LENGTH_DEFENSE: "Defense technique needs improvement on good length",
    WeaknessCategory.WIDE_OUTSIDE_OFF: "Struggles with wide deliveries outside off stump",
    WeaknessCategory.SPINNING_BALL_FOTWORK: "Footwork issues when facing spin bowling",
    WeaknessCategory.BACKLIFT_ANGLE_INCONSISTENT: "Inconsistent backlift angle affecting shot execution",
    WeaknessCategory.LATE_CONTACT_POINT: "Late contact point leading to timing issues",
    WeaknessCategory.HEAD_STABILITY: "Head movement affecting judgment and balance",
    WeaknessCategory.FOOTWORK_STABILITY: "Footwork instability affecting shot execution",
    WeaknessCategory.TIMING_CONSISTENCY: "Inconsistent timing across different deliveries",
}

def get_drills_for_weakness(weakness: WeaknessCategory) -> List[str]:
    """Get recommended drills for a weakness category"""
    return WEAKNESS_DRILLS.get(weakness, ["General batting practice"])

def get_focus_points_for_weakness(weakness: WeaknessCategory) -> List[str]:
    """Get focus points for a weakness category"""
    return WEAKNESS_FOCUS_POINTS.get(weakness, ["Focus on technique"])

def get_weakness_description(weakness: WeaknessCategory) -> str:
    """Get human-readable description of a weakness"""
    return WEAKNESS_DESCRIPTIONS.get(weakness, "Technique improvement needed")

