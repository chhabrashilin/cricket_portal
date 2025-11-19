from typing import Dict, Any, List, Optional
import numpy as np
import logging
from backend.models import DeliveryType, Line, ShotType, Outcome

logger = logging.getLogger(__name__)

class DeliveryClassifier:
    """Classify delivery type, shot type, and outcome from pose data"""
    
    def classify_delivery(self, pose_sequence: List[Dict], segment: Dict) -> Dict[str, Any]:
        """
        Classify a delivery/shot from pose sequence
        
        Args:
            pose_sequence: List of pose data for the segment
            segment: Segment metadata (start/end times)
            
        Returns:
            Dictionary with delivery classification
        """
        if not pose_sequence:
            return self._default_delivery()
        
        # Analyze pose sequence to infer delivery and shot
        delivery_type = self._infer_delivery_type(pose_sequence)
        line = self._infer_line(pose_sequence)
        shot_type = self._infer_shot_type(pose_sequence)
        outcome = self._infer_outcome(pose_sequence)
        
        # Calculate estimates
        ball_speed = self._estimate_ball_speed(pose_sequence)
        bat_speed = self._estimate_bat_speed(pose_sequence)
        rating = self._calculate_rating(pose_sequence, outcome)
        
        return {
            'inferred_delivery_type': delivery_type.value if delivery_type else None,
            'line': line.value if line else None,
            'shot_type': shot_type.value if shot_type else None,
            'outcome': outcome.value if outcome else None,
            'ball_speed_estimate': ball_speed,
            'bat_speed_estimate': bat_speed,
            'rating': rating,
            'score_zone': self._infer_score_zone(pose_sequence, shot_type)
        }
    
    def _infer_delivery_type(self, pose_sequence: List[Dict]) -> Optional[DeliveryType]:
        """Infer delivery type from pose sequence"""
        if len(pose_sequence) < 3:
            return None
        
        # Analyze bat hand trajectory
        bat_hand_y = [p['metrics'].get('bat_hand_y', 0.5) for p in pose_sequence if 'metrics' in p]
        if not bat_hand_y:
            return None
        
        # Low bat position early = short ball
        # High bat position early = full/yorker
        # Medium = good length
        
        min_y = min(bat_hand_y[:len(bat_hand_y)//3])  # First third
        max_y = max(bat_hand_y)
        y_range = max_y - min_y
        
        if min_y > 0.6:  # Bat starts high
            if y_range > 0.3:
                return DeliveryType.YORKER
            return DeliveryType.FULL
        elif min_y < 0.4:  # Bat starts low
            return DeliveryType.BOUNCER
        else:
            return DeliveryType.GOOD_LENGTH
    
    def _infer_line(self, pose_sequence: List[Dict]) -> Optional[Line]:
        """Infer line of delivery from pose"""
        if not pose_sequence:
            return None
        
        # Use head position and body alignment
        head_x = [p['metrics'].get('head_x', 0.5) for p in pose_sequence if 'metrics' in p]
        if not head_x:
            return None
        
        avg_head_x = np.mean(head_x)
        
        if avg_head_x < 0.4:
            return Line.WIDE_OFF
        elif avg_head_x < 0.45:
            return Line.OFF_STUMP
        elif avg_head_x < 0.55:
            return Line.MIDDLE
        elif avg_head_x < 0.6:
            return Line.LEG_STUMP
        else:
            return Line.WIDE_LEG
    
    def _infer_shot_type(self, pose_sequence: List[Dict]) -> Optional[ShotType]:
        """Infer shot type from bat trajectory"""
        if len(pose_sequence) < 3:
            return None
        
        bat_hand_x = [p['metrics'].get('bat_hand_x', 0.5) for p in pose_sequence if 'metrics' in p]
        bat_hand_y = [p['metrics'].get('bat_hand_y', 0.5) for p in pose_sequence if 'metrics' in p]
        
        if not bat_hand_x or not bat_hand_y:
            return None
        
        # Analyze trajectory
        x_range = max(bat_hand_x) - min(bat_hand_x)
        y_range = max(bat_hand_y) - min(bat_hand_y)
        
        # Horizontal movement = cut/pull
        if x_range > y_range * 1.5:
            if np.mean(bat_hand_x) > 0.5:
                return ShotType.CUT
            else:
                return ShotType.PULL
        # Vertical movement = drive/loft
        elif y_range > x_range * 1.5:
            if min(bat_hand_y) < 0.3:  # High backlift
                return ShotType.LOFTED
            return ShotType.DRIVE
        # Minimal movement = defense/leave
        elif x_range < 0.1 and y_range < 0.1:
            return ShotType.LEAVE
        else:
            return ShotType.DRIVE  # Default
    
    def _infer_outcome(self, pose_sequence: List[Dict]) -> Optional[Outcome]:
        """Infer outcome quality from pose metrics"""
        if not pose_sequence:
            return None
        
        # Analyze head stability, bat path smoothness
        head_x = [p['metrics'].get('head_x', 0.5) for p in pose_sequence if 'metrics' in p]
        head_stability = np.std(head_x) if head_x else 1.0
        
        # Analyze bat path
        bat_hand_x = [p['metrics'].get('bat_hand_x', 0.5) for p in pose_sequence if 'metrics' in p]
        bat_path_smoothness = np.std(np.diff(bat_hand_x)) if len(bat_hand_x) > 1 else 1.0
        
        # Good outcome = stable head, smooth bat path
        if head_stability < 0.05 and bat_path_smoothness < 0.1:
            return Outcome.MIDDLED
        elif head_stability < 0.1:
            return Outcome.MISHIT
        elif head_stability > 0.15:
            return Outcome.MISS
        else:
            return Outcome.EDGE
    
    def _estimate_ball_speed(self, pose_sequence: List[Dict]) -> Optional[float]:
        """Estimate ball speed (placeholder - would need ball tracking)"""
        # Placeholder: estimate based on delivery type
        if not pose_sequence:
            return None
        
        delivery_type = self._infer_delivery_type(pose_sequence)
        if delivery_type == DeliveryType.BOUNCER:
            return np.random.uniform(130, 150)  # km/h
        elif delivery_type == DeliveryType.YORKER:
            return np.random.uniform(140, 155)
        else:
            return np.random.uniform(120, 140)
    
    def _estimate_bat_speed(self, pose_sequence: List[Dict]) -> Optional[float]:
        """Estimate bat speed from swing"""
        if len(pose_sequence) < 2:
            return None
        
        bat_hand_x = [p['metrics'].get('bat_hand_x', 0.5) for p in pose_sequence if 'metrics' in p]
        if len(bat_hand_x) < 2:
            return None
        
        # Calculate velocity
        timestamps = [p['timestamp'] for p in pose_sequence]
        if len(timestamps) < 2:
            return None
        
        dt = timestamps[-1] - timestamps[0]
        if dt == 0:
            return None
        
        # Approximate speed (normalized coordinates to km/h)
        distance = max(bat_hand_x) - min(bat_hand_x)
        speed = (distance / dt) * 100  # Rough conversion
        
        return max(20, min(80, speed))  # Clamp to reasonable range
    
    def _calculate_rating(self, pose_sequence: List[Dict], outcome: Optional[Outcome]) -> float:
        """Calculate performance rating (0-10)"""
        if not outcome:
            return 5.0
        
        base_ratings = {
            Outcome.MIDDLED: 9.0,
            Outcome.MISHIT: 6.0,
            Outcome.EDGE: 4.0,
            Outcome.MISS: 2.0,
            Outcome.WICKET_RISK: 1.0
        }
        
        rating = base_ratings.get(outcome, 5.0)
        
        # Adjust based on head stability
        if pose_sequence:
            head_x = [p['metrics'].get('head_x', 0.5) for p in pose_sequence if 'metrics' in p]
            head_stability = 1.0 - min(1.0, np.std(head_x) * 10) if head_x else 0
            rating += head_stability * 0.5
        
        return max(0, min(10, rating))
    
    def _infer_score_zone(self, pose_sequence: List[Dict], shot_type: Optional[ShotType]) -> Optional[str]:
        """Infer score zone from shot type"""
        if not shot_type:
            return None
        
        zone_map = {
            ShotType.DRIVE: "mid_off",
            ShotType.CUT: "point",
            ShotType.PULL: "square_leg",
            ShotType.SWEEP: "fine_leg",
            ShotType.LOFTED: "long_on",
            ShotType.SLOG: "mid_wicket"
        }
        
        return zone_map.get(shot_type, "cover")
    
    def _default_delivery(self) -> Dict[str, Any]:
        """Return default delivery data"""
        return {
            'inferred_delivery_type': None,
            'line': None,
            'shot_type': None,
            'outcome': None,
            'ball_speed_estimate': None,
            'bat_speed_estimate': None,
            'rating': 5.0,
            'score_zone': None
        }

