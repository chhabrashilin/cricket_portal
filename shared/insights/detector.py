"""
Weakness detection engine.

Analyzes delivery patterns and metrics to identify specific weaknesses
based on thresholds and patterns.
"""
from typing import Dict, List, Optional, Tuple
from shared.types.enums import (
    WeaknessCategory, DeliveryType, ShotType, Outcome,
    Line
)
from shared.insights.weakness_mapping import (
    get_drills_for_weakness,
    get_focus_points_for_weakness,
    get_weakness_description
)

# Thresholds for weakness detection
WEAKNESS_THRESHOLDS = {
    WeaknessCategory.SHORT_BALL_PULL: {
        "middled_percentage": 0.40,  # < 40% middled = weakness
        "min_attempts": 5,
        "delivery_type": DeliveryType.SHORT,
        "shot_type": ShotType.PULL
    },
    WeaknessCategory.FULL_BALL_DRIVE: {
        "middled_percentage": 0.45,
        "min_attempts": 5,
        "delivery_type": DeliveryType.FULL,
        "shot_type": ShotType.DRIVE
    },
    WeaknessCategory.GOOD_LENGTH_DEFENSE: {
        "middled_percentage": 0.50,
        "min_attempts": 8,
        "delivery_type": DeliveryType.GOOD_LENGTH,
        "shot_type": ShotType.DEFENSE
    },
    WeaknessCategory.WIDE_OUTSIDE_OFF: {
        "middled_percentage": 0.35,
        "min_attempts": 5,
        "line": Line.WIDE_OFF,
        "shot_type": None  # Any shot type
    },
    WeaknessCategory.SPINNING_BALL_FOTWORK: {
        "middled_percentage": 0.40,
        "min_attempts": 5,
        "bowler_type": "spin",  # Special handling
        "shot_type": None
    },
    WeaknessCategory.BACKLIFT_ANGLE_INCONSISTENT: {
        "consistency_threshold": 0.15,  # Variance in backlift angle
        "min_deliveries": 10
    },
    WeaknessCategory.LATE_CONTACT_POINT: {
        "timing_variance": 0.20,  # High variance in contact timing
        "min_deliveries": 10
    },
    WeaknessCategory.HEAD_STABILITY: {
        "stability_score": 0.70,  # < 0.70 = weakness
        "min_deliveries": 10
    },
    WeaknessCategory.FOOTWORK_STABILITY: {
        "stability_score": 0.70,
        "min_deliveries": 10
    },
    WeaknessCategory.TIMING_CONSISTENCY: {
        "consistency_score": 0.65,
        "min_deliveries": 10
    },
}

class WeaknessDetector:
    """
    Detects weaknesses from delivery patterns and metrics.
    
    Uses threshold-based detection and pattern analysis to identify
    specific areas for improvement.
    """
    
    def __init__(self):
        self.thresholds = WEAKNESS_THRESHOLDS
    
    def detect_weaknesses(
        self,
        metric_breakdown: Dict,
        deliveries: List[Dict]
    ) -> List[Dict]:
        """
        Detect weaknesses from metric breakdown and delivery data.
        
        Args:
            metric_breakdown: Aggregated metrics from analysis
            deliveries: List of delivery dictionaries
            
        Returns:
            List of weakness dictionaries with evidence and recommendations
        """
        weaknesses = []
        
        # Check combination-based weaknesses
        combinations = metric_breakdown.get("combinations", {})
        for combo_key, combo_data in combinations.items():
            weakness = self._check_combination_weakness(combo_key, combo_data)
            if weakness:
                weaknesses.append(weakness)
        
        # Check metric-based weaknesses
        metric_weaknesses = self._check_metric_weaknesses(metric_breakdown, deliveries)
        weaknesses.extend(metric_weaknesses)
        
        return weaknesses
    
    def _check_combination_weakness(
        self,
        combo_key: str,
        combo_data: Dict
    ) -> Optional[Dict]:
        """
        Check if a delivery/shot combination indicates a weakness.
        
        Args:
            combo_key: Format "delivery_type_shot_type"
            combo_data: Statistics for this combination
            
        Returns:
            Weakness dict if detected, None otherwise
        """
        attempts = combo_data.get("attempts", 0)
        if attempts < 5:  # Need minimum sample size
            return None
        
        middled = combo_data.get("middled", 0)
        middled_pct = middled / attempts if attempts > 0 else 0
        
        # Map combination to weakness category
        weakness_category = self._map_combination_to_weakness(combo_key)
        if not weakness_category:
            return None
        
        threshold = self.thresholds.get(weakness_category, {}).get("middled_percentage", 0.40)
        
        if middled_pct < threshold:
            return {
                "tag": weakness_category.value,
                "category": weakness_category,
                "description": self._describe_combination_weakness(
                    combo_key, combo_data, middled_pct
                ),
                "evidence": {
                    "attempts": attempts,
                    "middled": middled,
                    "edges": combo_data.get("edges", 0),
                    "mishits": combo_data.get("mishits", 0),
                    "misses": combo_data.get("misses", 0),
                    "middled_percentage": middled_pct
                },
                "severity": self._calculate_severity(middled_pct, threshold),
                "recommendations": {
                    "drills": get_drills_for_weakness(weakness_category),
                    "focus_points": get_focus_points_for_weakness(weakness_category)
                }
            }
        
        return None
    
    def _map_combination_to_weakness(self, combo_key: str) -> Optional[WeaknessCategory]:
        """Map a combination key to a weakness category"""
        key_lower = combo_key.lower()
        
        if "short" in key_lower and "pull" in key_lower:
            return WeaknessCategory.SHORT_BALL_PULL
        elif "full" in key_lower and "drive" in key_lower:
            return WeaknessCategory.FULL_BALL_DRIVE
        elif "good_length" in key_lower and "defense" in key_lower:
            return WeaknessCategory.GOOD_LENGTH_DEFENSE
        elif "wide" in key_lower and "off" in key_lower:
            return WeaknessCategory.WIDE_OUTSIDE_OFF
        
        return None
    
    def _check_metric_weaknesses(
        self,
        metric_breakdown: Dict,
        deliveries: List[Dict]
    ) -> List[Dict]:
        """Check metric-based weaknesses"""
        weaknesses = []
        
        # Check head stability
        head_stability = metric_breakdown.get("head_stability_score")
        if head_stability is not None and head_stability < 0.70:
            weaknesses.append(self._create_metric_weakness(
                WeaknessCategory.HEAD_STABILITY,
                head_stability,
                "Head stability score is below optimal"
            ))
        
        # Check footwork stability
        footwork_stability = metric_breakdown.get("footwork_stability_score")
        if footwork_stability is not None and footwork_stability < 0.70:
            weaknesses.append(self._create_metric_weakness(
                WeaknessCategory.FOOTWORK_STABILITY,
                footwork_stability,
                "Footwork stability needs improvement"
            ))
        
        # Check timing consistency
        timing_consistency = metric_breakdown.get("timing_consistency")
        if timing_consistency is not None and timing_consistency < 0.65:
            weaknesses.append(self._create_metric_weakness(
                WeaknessCategory.TIMING_CONSISTENCY,
                timing_consistency,
                "Timing consistency is below optimal"
            ))
        
        return weaknesses
    
    def _create_metric_weakness(
        self,
        category: WeaknessCategory,
        score: float,
        description: str
    ) -> Dict:
        """Create a weakness dict for metric-based weakness"""
        return {
            "tag": category.value,
            "category": category,
            "description": f"{description} (score: {score:.2f})",
            "evidence": {
                "score": score,
                "threshold": self.thresholds.get(category, {}).get(
                    "stability_score", 0.70
                )
            },
            "severity": "medium" if score > 0.50 else "high",
            "recommendations": {
                "drills": get_drills_for_weakness(category),
                "focus_points": get_focus_points_for_weakness(category)
            }
        }
    
    def _describe_combination_weakness(
        self,
        combo_key: str,
        combo_data: Dict,
        middled_pct: float
    ) -> str:
        """Generate natural language description of combination weakness"""
        attempts = combo_data.get("attempts", 0)
        middled = combo_data.get("middled", 0)
        edges = combo_data.get("edges", 0)
        mishits = combo_data.get("mishits", 0)
        
        delivery_type, shot_type = combo_key.split("_", 1) if "_" in combo_key else (combo_key, "")
        
        desc = f"You attempted {attempts} {shot_type.replace('_', ' ')} shots to {delivery_type.replace('_', ' ')} deliveries. "
        desc += f"Only {middled} ({middled_pct*100:.1f}%) were cleanly timed. "
        
        if edges > 0:
            desc += f"{edges} resulted in edges. "
        if mishits > 0:
            desc += f"{mishits} were mishit. "
        
        return desc.strip()
    
    def _calculate_severity(self, middled_pct: float, threshold: float) -> str:
        """Calculate severity based on how far below threshold"""
        if middled_pct < threshold * 0.5:
            return "high"
        elif middled_pct < threshold * 0.75:
            return "medium"
        else:
            return "low"

