"""
Shared enums used across services
"""
from enum import Enum

class UserRole(str, Enum):
    """User roles in the system"""
    PLAYER = "player"
    COACH = "coach"
    ADMIN = "admin"

class Handedness(str, Enum):
    """Batting handedness"""
    LEFT = "left"
    RIGHT = "right"

class ExperienceLevel(str, Enum):
    """Player experience level"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    PROFESSIONAL = "professional"

class PlayStyle(str, Enum):
    """Playing style"""
    AGGRESSIVE = "aggressive"
    DEFENSIVE = "defensive"
    BALANCED = "balanced"
    COUNTER_ATTACKING = "counter_attacking"

class ProcessingStatus(str, Enum):
    """Session processing status"""
    PENDING = "pending"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"

class DeliveryType(str, Enum):
    """Cricket delivery types"""
    SHORT = "short"
    GOOD_LENGTH = "good_length"
    FULL = "full"
    YORKER = "yorker"
    BOUNCER = "bouncer"

class Line(str, Enum):
    """Delivery line"""
    OFF_STUMP = "off_stump"
    MIDDLE = "middle"
    LEG_STUMP = "leg_stump"
    WIDE_OFF = "wide_off"
    WIDE_LEG = "wide_leg"

class ShotType(str, Enum):
    """Cricket shot types"""
    DRIVE = "drive"
    PULL = "pull"
    CUT = "cut"
    SWEEP = "sweep"
    DEFENSE = "defense"
    LOFTED = "lofted"
    SLOG = "slog"
    LEAVE = "leave"
    HOOK = "hook"
    PUNCH = "punch"
    GLANCE = "glance"

class Outcome(str, Enum):
    """Shot outcome"""
    MIDDLED = "middled"
    EDGE = "edge"
    MISHIT = "mishit"
    MISS = "miss"
    WICKET_RISK = "wicket_risk"

class BowlerType(str, Enum):
    """Bowler type"""
    PACE = "pace"
    SPIN = "spin"
    MEDIUM = "medium"

class Surface(str, Enum):
    """Pitch surface type"""
    TURF = "turf"
    CEMENT = "cement"
    ASTRO = "astro"
    MAT = "mat"

class WeaknessCategory(str, Enum):
    """Weakness categories"""
    SHORT_BALL_PULL = "short_ball_pull"
    FULL_BALL_DRIVE = "full_ball_drive"
    GOOD_LENGTH_DEFENSE = "good_length_defense"
    WIDE_OUTSIDE_OFF = "wide_outside_off"
    SPINNING_BALL_FOOTWORK = "spinning_ball_footwork"
    BACKLIFT_ANGLE_INCONSISTENT = "backlift_angle_inconsistent"
    LATE_CONTACT_POINT = "late_contact_point"
    HEAD_STABILITY = "head_stability"
    FOOTWORK_STABILITY = "footwork_stability"
    TIMING_CONSISTENCY = "timing_consistency"

