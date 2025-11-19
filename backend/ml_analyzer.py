import cv2
import mediapipe as mp
import numpy as np
from typing import Dict, List, Any, Tuple
import math

class CricketBattingAnalyzer:
    """
    Advanced ML-based cricket batting analysis system.
    Analyzes pose, swing, footwork, balance, and timing to identify weaknesses.
    """
    
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Key landmark indices for cricket analysis
        self.landmarks = {
            'nose': 0,
            'left_shoulder': 11,
            'right_shoulder': 12,
            'left_elbow': 13,
            'right_elbow': 14,
            'left_wrist': 15,
            'right_wrist': 16,
            'left_hip': 23,
            'right_hip': 24,
            'left_knee': 25,
            'right_knee': 26,
            'left_ankle': 27,
            'right_ankle': 28,
        }
        
        # Ideal angles and positions for cricket batting
        self.ideal_metrics = {
            'backlift_angle': 45,  # degrees
            'head_position_stability': 0.05,  # max deviation in normalized coordinates
            'front_foot_placement': 0.3,  # normalized distance from stumps
            'balance_center': 0.5,  # center of mass position
            'swing_timing': 0.6,  # optimal contact point (0-1 of swing)
        }
    
    def analyze_batting(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main analysis function that processes extracted features and identifies weaknesses.
        
        Args:
            features: Dictionary containing pose data, keyframes, and video metadata
            
        Returns:
            Dictionary with overall score, weaknesses, strengths, and recommendations
        """
        pose_data = features.get('pose_data', [])
        keyframes = features.get('keyframes', {})
        video_metadata = features.get('metadata', {})
        
        if not pose_data:
            return self._empty_analysis()
        
        # Extract metrics from pose data
        metrics = self._extract_metrics(pose_data, keyframes)
        
        # Analyze each aspect of batting
        analyses = {
            'footwork': self._analyze_footwork(pose_data, metrics),
            'balance': self._analyze_balance(pose_data, metrics),
            'head_position': self._analyze_head_position(pose_data, metrics),
            'swing_path': self._analyze_swing_path(pose_data, metrics),
            'timing': self._analyze_timing(pose_data, metrics, keyframes),
            'backlift': self._analyze_backlift(pose_data, metrics),
            'follow_through': self._analyze_follow_through(pose_data, metrics),
        }
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(analyses)
        
        # Identify weaknesses
        weaknesses = self._identify_weaknesses(analyses, metrics)
        
        # Identify strengths
        strengths = self._identify_strengths(analyses, metrics)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(weaknesses, analyses)
        
        return {
            'overall_score': overall_score,
            'weaknesses': weaknesses,
            'strengths': strengths,
            'recommendations': recommendations,
            'detailed_metrics': {
                'analyses': analyses,
                'raw_metrics': metrics,
                'video_metadata': video_metadata
            }
        }
    
    def _extract_metrics(self, pose_data: List[Dict], keyframes: Dict) -> Dict[str, Any]:
        """Extract key metrics from pose data"""
        metrics = {
            'head_positions': [],
            'shoulder_angles': [],
            'hip_positions': [],
            'ankle_positions': [],
            'knee_angles': [],
            'wrist_positions': [],
            'center_of_mass': [],
            'swing_phases': [],
        }
        
        for frame_data in pose_data:
            landmarks = frame_data.get('landmarks', {})
            if not landmarks:
                continue
            
            # Head position (using nose as proxy)
            if 'nose' in landmarks:
                metrics['head_positions'].append(landmarks['nose'])
            
            # Shoulder alignment
            if 'left_shoulder' in landmarks and 'right_shoulder' in landmarks:
                shoulder_angle = self._calculate_angle(
                    landmarks['left_shoulder'],
                    landmarks['right_shoulder']
                )
                metrics['shoulder_angles'].append(shoulder_angle)
            
            # Hip positions
            if 'left_hip' in landmarks and 'right_hip' in landmarks:
                hip_center = self._midpoint(
                    landmarks['left_hip'],
                    landmarks['right_hip']
                )
                metrics['hip_positions'].append(hip_center)
            
            # Ankle positions (footwork)
            if 'left_ankle' in landmarks and 'right_ankle' in landmarks:
                metrics['ankle_positions'].append({
                    'left': landmarks['left_ankle'],
                    'right': landmarks['right_ankle']
                })
            
            # Wrist positions (for swing analysis)
            if 'left_wrist' in landmarks and 'right_wrist' in landmarks:
                # Use the wrist that's higher (likely the bat hand)
                wrist_pos = landmarks['left_wrist'] if landmarks['left_wrist'][1] < landmarks['right_wrist'][1] else landmarks['right_wrist']
                metrics['wrist_positions'].append((wrist_pos[0], wrist_pos[1]))
            
            # Center of mass (approximate)
            if all(k in landmarks for k in ['left_hip', 'right_hip', 'left_shoulder', 'right_shoulder']):
                com = self._calculate_center_of_mass(landmarks)
                metrics['center_of_mass'].append(com)
        
        return metrics
    
    def _analyze_footwork(self, pose_data: List[Dict], metrics: Dict) -> Dict[str, Any]:
        """Analyze footwork quality"""
        if not metrics.get('ankle_positions'):
            return {'score': 0, 'issues': ['Insufficient data']}
        
        issues = []
        score = 100
        
        # Check front foot movement
        ankle_positions = metrics['ankle_positions']
        if len(ankle_positions) < 2:
            return {'score': 0, 'issues': ['Insufficient frames']}
        
        # Determine front foot (usually moves forward more)
        initial_left = ankle_positions[0]['left']
        initial_right = ankle_positions[0]['right']
        final_left = ankle_positions[-1]['left']
        final_right = ankle_positions[-1]['right']
        
        left_movement = abs(final_left[0] - initial_left[0])
        right_movement = abs(final_right[0] - initial_right[0])
        
        # Front foot should move forward significantly
        if max(left_movement, right_movement) < 0.1:  # normalized coordinates
            issues.append("Limited front foot movement - may struggle with forward defense")
            score -= 30
        
        # Check foot spacing (should be shoulder-width or wider)
        avg_spacing = np.mean([
            abs(pos['left'][0] - pos['right'][0]) 
            for pos in ankle_positions
        ])
        
        if avg_spacing < 0.15:
            issues.append("Feet too close together - affects balance and power")
            score -= 20
        
        # Check if back foot stays grounded (for most shots)
        back_foot_lift = max(
            abs(final_left[1] - initial_left[1]),
            abs(final_right[1] - initial_right[1])
        )
        
        if back_foot_lift > 0.15:
            issues.append("Excessive back foot lift - may indicate poor weight transfer")
            score -= 15
        
        return {
            'score': max(0, score),
            'issues': issues,
            'front_foot_movement': max(left_movement, right_movement),
            'foot_spacing': avg_spacing
        }
    
    def _analyze_balance(self, pose_data: List[Dict], metrics: Dict) -> Dict[str, Any]:
        """Analyze balance and stability"""
        if not metrics.get('center_of_mass'):
            return {'score': 0, 'issues': ['Insufficient data']}
        
        com_positions = metrics['center_of_mass']
        issues = []
        score = 100
        
        # Check center of mass stability
        com_x = [pos[0] for pos in com_positions]
        com_y = [pos[1] for pos in com_positions]
        
        x_variance = np.var(com_x)
        y_variance = np.var(com_y)
        
        # High variance indicates instability
        if x_variance > 0.01:
            issues.append("Excessive lateral movement - balance issues")
            score -= 25
        
        if y_variance > 0.01:
            issues.append("Excessive vertical movement - may be off-balance")
            score -= 25
        
        # Check if center of mass is too far forward or back
        avg_com_x = np.mean(com_x)
        if avg_com_x < 0.4:
            issues.append("Weight too far back - may struggle with forward shots")
            score -= 15
        elif avg_com_x > 0.6:
            issues.append("Weight too far forward - vulnerable to short-pitched deliveries")
            score -= 15
        
        return {
            'score': max(0, score),
            'issues': issues,
            'stability': 1.0 / (1.0 + x_variance + y_variance)
        }
    
    def _analyze_head_position(self, pose_data: List[Dict], metrics: Dict) -> Dict[str, Any]:
        """Analyze head position and stability"""
        if not metrics.get('head_positions'):
            return {'score': 0, 'issues': ['Insufficient data']}
        
        head_positions = metrics['head_positions']
        issues = []
        score = 100
        
        # Check head stability (should be relatively still)
        head_x = [pos[0] for pos in head_positions]
        head_y = [pos[1] for pos in head_positions]
        
        x_variance = np.var(head_x)
        y_variance = np.var(head_y)
        
        if x_variance > self.ideal_metrics['head_position_stability']:
            issues.append("Head moving too much laterally - affects judgment and timing")
            score -= 30
        
        if y_variance > self.ideal_metrics['head_position_stability']:
            issues.append("Head bobbing up and down - poor technique")
            score -= 30
        
        # Check if head is too far forward or back
        avg_head_x = np.mean(head_x)
        if avg_head_x < 0.45:
            issues.append("Head position too far back - may struggle to get to pitch of ball")
            score -= 20
        elif avg_head_x > 0.55:
            issues.append("Head falling over - balance issue")
            score -= 20
        
        return {
            'score': max(0, score),
            'issues': issues,
            'stability': 1.0 / (1.0 + x_variance + y_variance)
        }
    
    def _analyze_swing_path(self, pose_data: List[Dict], metrics: Dict) -> Dict[str, Any]:
        """Analyze bat swing path"""
        if not metrics.get('wrist_positions'):
            return {'score': 0, 'issues': ['Insufficient data']}
        
        issues = []
        score = 100
        
        # Analyze wrist trajectory (proxy for bat path)
        wrist_positions = metrics.get('wrist_positions', [])
        if len(wrist_positions) < 3:
            return {'score': 0, 'issues': ['Insufficient frames']}
        
        # Check for straight bat path (should be relatively straight for defensive shots)
        # For attacking shots, check for proper arc
        
        # Calculate swing arc
        positions = np.array(wrist_positions)
        if len(positions) > 2:
            # Check if swing is too horizontal (cross-bat shots)
            y_range = np.max(positions[:, 1]) - np.min(positions[:, 1])
            x_range = np.max(positions[:, 0]) - np.min(positions[:, 0])
            
            if x_range > y_range * 1.5:
                issues.append("Swing path too horizontal - risk of edges")
                score -= 25
            
            # Check for proper follow-through
            if len(positions) > 5:
                final_movement = positions[-1] - positions[-5]
                if np.linalg.norm(final_movement) < 0.05:
                    issues.append("Incomplete follow-through - may lack power")
                    score -= 15
        
        return {
            'score': max(0, score),
            'issues': issues
        }
    
    def _analyze_timing(self, pose_data: List[Dict], metrics: Dict, keyframes: Dict) -> Dict[str, Any]:
        """Analyze timing of the shot"""
        issues = []
        score = 100
        
        # Timing analysis requires ball tracking (advanced feature)
        # For now, analyze based on swing smoothness and consistency
        
        if len(pose_data) < 10:
            return {'score': 0, 'issues': ['Insufficient data']}
        
        # Check for jerky movements (indicates poor timing)
        wrist_positions = metrics.get('wrist_positions', [])
        if len(wrist_positions) > 3:
            velocities = []
            for i in range(1, len(wrist_positions)):
                vel = np.linalg.norm(
                    np.array(wrist_positions[i]) - np.array(wrist_positions[i-1])
                )
                velocities.append(vel)
            
            # High variance in velocity indicates inconsistent timing
            if len(velocities) > 1 and np.var(velocities) > 0.01:
                issues.append("Inconsistent swing speed - timing issues")
                score -= 20
        
        return {
            'score': max(0, score),
            'issues': issues
        }
    
    def _analyze_backlift(self, pose_data: List[Dict], metrics: Dict) -> Dict[str, Any]:
        """Analyze backlift angle and position"""
        issues = []
        score = 100
        
        # Backlift analysis requires bat detection (advanced)
        # For now, use wrist position as proxy
        
        wrist_positions = metrics.get('wrist_positions', [])
        if len(wrist_positions) < 2:
            return {'score': 0, 'issues': ['Insufficient data']}
        
        # Check initial backlift position
        initial_wrist = wrist_positions[0]
        if len(wrist_positions) > 5:
            early_wrist = wrist_positions[2]
            
            # Calculate angle (simplified)
            if initial_wrist[1] > early_wrist[1] + 0.1:
                issues.append("Backlift may be too low - limits shot options")
                score -= 15
        
        return {
            'score': max(0, score),
            'issues': issues
        }
    
    def _analyze_follow_through(self, pose_data: List[Dict], metrics: Dict) -> Dict[str, Any]:
        """Analyze follow-through quality"""
        issues = []
        score = 100
        
        wrist_positions = metrics.get('wrist_positions', [])
        if len(wrist_positions) < 5:
            return {'score': 0, 'issues': ['Insufficient data']}
        
        # Check if follow-through is complete
        final_positions = wrist_positions[-3:]
        movement = np.mean([
            np.linalg.norm(final_positions[i] - final_positions[i-1])
            for i in range(1, len(final_positions))
        ])
        
        if movement < 0.02:
            issues.append("Incomplete follow-through - may indicate defensive mindset or lack of commitment")
            score -= 20
        
        return {
            'score': max(0, score),
            'issues': issues
        }
    
    def _calculate_overall_score(self, analyses: Dict[str, Dict]) -> float:
        """Calculate weighted overall score"""
        weights = {
            'footwork': 0.15,
            'balance': 0.20,
            'head_position': 0.20,
            'swing_path': 0.15,
            'timing': 0.15,
            'backlift': 0.10,
            'follow_through': 0.05,
        }
        
        total_score = 0
        total_weight = 0
        
        for aspect, analysis in analyses.items():
            if aspect in weights:
                score = analysis.get('score', 0)
                weight = weights[aspect]
                total_score += score * weight
                total_weight += weight
        
        return round(total_score / total_weight if total_weight > 0 else 0, 2)
    
    def _identify_weaknesses(self, analyses: Dict[str, Dict], metrics: Dict) -> List[Dict[str, Any]]:
        """Identify and categorize weaknesses"""
        weaknesses = []
        
        for aspect, analysis in analyses.items():
            score = analysis.get('score', 100)
            issues = analysis.get('issues', [])
            
            if score < 70:  # Threshold for weakness
                severity = "high" if score < 50 else "medium" if score < 60 else "low"
                
                for issue in issues:
                    weaknesses.append({
                        'category': aspect,
                        'severity': severity,
                        'description': issue,
                        'confidence': 1.0 - (score / 100),
                        'score': score
                    })
        
        # Sort by severity and confidence
        weaknesses.sort(key=lambda x: (
            {'high': 0, 'medium': 1, 'low': 2}[x['severity']],
            -x['confidence']
        ))
        
        return weaknesses
    
    def _identify_strengths(self, analyses: Dict[str, Dict], metrics: Dict) -> List[Dict[str, Any]]:
        """Identify strengths"""
        strengths = []
        
        for aspect, analysis in analyses.items():
            score = analysis.get('score', 0)
            
            if score >= 80:  # Threshold for strength
                strengths.append({
                    'category': aspect,
                    'description': f"Strong {aspect.replace('_', ' ')} technique",
                    'score': score
                })
        
        return strengths
    
    def _generate_recommendations(self, weaknesses: List[Dict], analyses: Dict[str, Dict]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Group weaknesses by category
        category_issues = {}
        for weakness in weaknesses:
            cat = weakness['category']
            if cat not in category_issues:
                category_issues[cat] = []
            category_issues[cat].append(weakness)
        
        # Generate specific recommendations
        recommendation_map = {
            'footwork': [
                "Practice front foot movement drills - focus on getting forward to the pitch of the ball",
                "Work on maintaining proper foot spacing (shoulder-width apart)",
                "Practice keeping back foot grounded for better balance and power transfer"
            ],
            'balance': [
                "Focus on maintaining a stable center of mass throughout the shot",
                "Practice balance exercises and core strengthening",
                "Work on weight transfer from back foot to front foot"
            ],
            'head_position': [
                "Keep your head still and in line with the ball",
                "Practice head position drills - focus on keeping head over the ball",
                "Avoid excessive head movement which affects judgment"
            ],
            'swing_path': [
                "Work on straight bat shots - practice playing with a straight bat",
                "Focus on proper bat path - avoid cross-bat shots",
                "Practice follow-through to ensure complete shots"
            ],
            'timing': [
                "Practice with a bowling machine or throwdowns to improve timing",
                "Focus on watching the ball closely and playing late",
                "Work on consistent swing speed and rhythm"
            ],
            'backlift': [
                "Practice maintaining a good backlift position",
                "Work on getting the bat into position early",
                "Focus on backlift angle - should be around 45 degrees"
            ],
            'follow_through': [
                "Complete your shots with a full follow-through",
                "Practice committing to shots fully",
                "Work on maintaining bat speed through the shot"
            ]
        }
        
        for category, issues in category_issues.items():
            if category in recommendation_map:
                # Get the most severe issue
                most_severe = max(issues, key=lambda x: {'high': 0, 'medium': 1, 'low': 2}[x['severity']])
                if most_severe['severity'] in ['high', 'medium']:
                    recommendations.extend(recommendation_map[category][:2])
                else:
                    recommendations.append(recommendation_map[category][0])
        
        # Add general recommendations if overall score is low
        if len(weaknesses) > 3:
            recommendations.append("Consider working with a qualified cricket coach for comprehensive technique improvement")
            recommendations.append("Practice regularly with focus on one aspect at a time")
        
        return list(set(recommendations))  # Remove duplicates
    
    def _empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis when no data available"""
        return {
            'overall_score': 0,
            'weaknesses': [{
                'category': 'data',
                'severity': 'high',
                'description': 'Insufficient video data for analysis',
                'confidence': 1.0
            }],
            'strengths': [],
            'recommendations': ['Please ensure video contains clear view of batting stance and swing'],
            'detailed_metrics': {}
        }
    
    # Helper methods
    def _calculate_angle(self, point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
        """Calculate angle between two points"""
        return math.degrees(math.atan2(point2[1] - point1[1], point2[0] - point1[0]))
    
    def _midpoint(self, point1: Tuple[float, float], point2: Tuple[float, float]) -> Tuple[float, float]:
        """Calculate midpoint between two points"""
        return ((point1[0] + point2[0]) / 2, (point1[1] + point2[1]) / 2)
    
    def _calculate_center_of_mass(self, landmarks: Dict) -> Tuple[float, float]:
        """Calculate approximate center of mass"""
        key_points = ['left_hip', 'right_hip', 'left_shoulder', 'right_shoulder']
        points = [landmarks[k] for k in key_points if k in landmarks]
        
        if not points:
            return (0.5, 0.5)
        
        return (
            np.mean([p[0] for p in points]),
            np.mean([p[1] for p in points])
        )

