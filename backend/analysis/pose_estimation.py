import mediapipe as mp
import cv2
import numpy as np
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class PoseEstimator:
    """Estimate human pose from video frames using MediaPipe"""
    
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            model_complexity=2  # Higher accuracy
        )
        
        # Key landmark indices for cricket analysis
        self.landmark_map = {
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
    
    def estimate_pose(self, frame: np.ndarray) -> Optional[Dict[str, Any]]:
        """
        Estimate pose from a single frame
        
        Returns:
            Dictionary with landmarks and derived metrics, or None if no pose detected
        """
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process with MediaPipe
        results = self.pose.process(rgb_frame)
        
        if not results.pose_landmarks:
            return None
        
        # Extract landmarks
        landmarks = {}
        for name, idx in self.landmark_map.items():
            landmark = results.pose_landmarks.landmark[idx]
            landmarks[name] = {
                'x': landmark.x,
                'y': landmark.y,
                'z': landmark.z if hasattr(landmark, 'z') else 0,
                'visibility': landmark.visibility
            }
        
        # Calculate derived metrics
        metrics = self._calculate_metrics(landmarks)
        
        return {
            'landmarks': landmarks,
            'metrics': metrics
        }
    
    def _calculate_metrics(self, landmarks: Dict) -> Dict[str, float]:
        """Calculate cricket-specific metrics from landmarks"""
        metrics = {}
        
        # Head position (using nose)
        if 'nose' in landmarks:
            metrics['head_x'] = landmarks['nose']['x']
            metrics['head_y'] = landmarks['nose']['y']
        
        # Shoulder alignment
        if 'left_shoulder' in landmarks and 'right_shoulder' in landmarks:
            ls = landmarks['left_shoulder']
            rs = landmarks['right_shoulder']
            metrics['shoulder_angle'] = np.arctan2(
                rs['y'] - ls['y'],
                rs['x'] - ls['x']
            ) * 180 / np.pi
        
        # Hip position (center of mass approximation)
        if all(k in landmarks for k in ['left_hip', 'right_hip']):
            lh = landmarks['left_hip']
            rh = landmarks['right_hip']
            metrics['hip_center_x'] = (lh['x'] + rh['x']) / 2
            metrics['hip_center_y'] = (lh['y'] + rh['y']) / 2
        
        # Foot positions (for footwork analysis)
        if 'left_ankle' in landmarks and 'right_ankle' in landmarks:
            la = landmarks['left_ankle']
            ra = landmarks['right_ankle']
            metrics['foot_spacing'] = abs(la['x'] - ra['x'])
            metrics['front_foot_x'] = max(la['x'], ra['x'])  # Front foot is further forward
            metrics['back_foot_x'] = min(la['x'], ra['x'])
        
        # Wrist positions (for bat tracking)
        if 'left_wrist' in landmarks and 'right_wrist' in landmarks:
            lw = landmarks['left_wrist']
            rw = landmarks['right_wrist']
            # Use the higher wrist (likely bat hand)
            if lw['y'] < rw['y']:
                metrics['bat_hand_x'] = lw['x']
                metrics['bat_hand_y'] = lw['y']
            else:
                metrics['bat_hand_x'] = rw['x']
                metrics['bat_hand_y'] = rw['y']
        
        # Calculate stride (distance between feet)
        if 'left_ankle' in landmarks and 'right_ankle' in landmarks:
            la = landmarks['left_ankle']
            ra = landmarks['right_ankle']
            metrics['stride_length'] = np.sqrt(
                (la['x'] - ra['x'])**2 + (la['y'] - ra['y'])**2
            )
        
        return metrics
    
    def process_frames(self, frames: List[Dict]) -> List[Dict[str, Any]]:
        """
        Process multiple frames and return pose data
        
        Args:
            frames: List of frame dictionaries with 'frame' key
            
        Returns:
            List of pose data dictionaries
        """
        pose_data = []
        
        for frame_data in frames:
            pose = self.estimate_pose(frame_data['frame'])
            if pose:
                pose_data.append({
                    'frame_index': frame_data['frame_index'],
                    'timestamp': frame_data['timestamp'],
                    **pose
                })
        
        logger.info(f"Processed {len(pose_data)} frames with pose data out of {len(frames)} total")
        return pose_data

