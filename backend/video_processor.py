import cv2
import mediapipe as mp
import numpy as np
import os
import aiofiles
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

class VideoProcessor:
    """
    Handles video upload, storage, and feature extraction for ML analysis.
    """
    
    def __init__(self):
        self.upload_dir = "uploads/videos"
        self.processed_dir = "uploads/processed"
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Create directories if they don't exist
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)
    
    async def save_video(self, file) -> str:
        """Save uploaded video file"""
        # Generate unique filename
        file_ext = os.path.splitext(file.filename)[1] if file.filename else '.mp4'
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(self.upload_dir, unique_filename)
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        return file_path
    
    async def process_video(self, video_path: str) -> Dict[str, Any]:
        """
        Process video and extract features for ML analysis.
        Returns pose data, keyframes, and metadata.
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
        
        # Get video metadata
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = frame_count / fps if fps > 0 else 0
        
        metadata = {
            'fps': fps,
            'frame_count': frame_count,
            'width': width,
            'height': height,
            'duration': duration
        }
        
        # Process frames (sample every Nth frame for efficiency)
        frame_skip = max(1, int(fps / 10))  # Process ~10 frames per second
        pose_data = []
        keyframes = {
            'start': None,
            'backlift': None,
            'contact': None,
            'follow_through': None,
            'end': None
        }
        
        frame_idx = 0
        processed_frames = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Process every Nth frame
            if frame_idx % frame_skip == 0:
                # Convert BGR to RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Process with MediaPipe
                results = self.pose.process(rgb_frame)
                
                if results.pose_landmarks:
                    # Extract landmarks
                    landmarks = self._extract_landmarks(
                        results.pose_landmarks,
                        width,
                        height
                    )
                    
                    timestamp = frame_idx / fps if fps > 0 else 0
                    
                    pose_data.append({
                        'frame': processed_frames,
                        'timestamp': timestamp,
                        'landmarks': landmarks
                    })
                    
                    # Detect keyframes
                    self._detect_keyframes(
                        landmarks,
                        timestamp,
                        keyframes,
                        processed_frames
                    )
                    
                    processed_frames += 1
            
            frame_idx += 1
        
        cap.release()
        
        # If no pose detected, return minimal data
        if not pose_data:
            return {
                'pose_data': [],
                'keyframes': {},
                'metadata': metadata,
                'error': 'No pose detected in video'
            }
        
        return {
            'pose_data': pose_data,
            'keyframes': keyframes,
            'metadata': metadata
        }
    
    def _extract_landmarks(
        self,
        pose_landmarks,
        width: int,
        height: int
    ) -> Dict[str, tuple]:
        """Extract and normalize landmark positions"""
        landmarks = {}
        
        landmark_map = {
            0: 'nose',
            11: 'left_shoulder',
            12: 'right_shoulder',
            13: 'left_elbow',
            14: 'right_elbow',
            15: 'left_wrist',
            16: 'right_wrist',
            23: 'left_hip',
            24: 'right_hip',
            25: 'left_knee',
            26: 'right_knee',
            27: 'left_ankle',
            28: 'right_ankle',
        }
        
        for idx, landmark in enumerate(pose_landmarks.landmark):
            if idx in landmark_map:
                # Normalize coordinates (0-1 range)
                landmarks[landmark_map[idx]] = (
                    landmark.x,
                    landmark.y,
                    landmark.z if hasattr(landmark, 'z') else 0
                )
        
        return landmarks
    
    def _detect_keyframes(
        self,
        landmarks: Dict[str, tuple],
        timestamp: float,
        keyframes: Dict,
        frame_idx: int
    ):
        """Detect key moments in batting (start, backlift, contact, follow-through)"""
        # Start frame (first frame with pose)
        if keyframes['start'] is None:
            keyframes['start'] = {'timestamp': timestamp, 'frame': frame_idx}
        
        # Detect backlift (wrist at highest point)
        if 'left_wrist' in landmarks and 'right_wrist' in landmarks:
            wrist_y = min(landmarks['left_wrist'][1], landmarks['right_wrist'][1])
            
            if keyframes['backlift'] is None or \
               wrist_y < keyframes['backlift'].get('wrist_y', 1.0):
                keyframes['backlift'] = {
                    'timestamp': timestamp,
                    'frame': frame_idx,
                    'wrist_y': wrist_y
                }
        
        # Contact point (wrist at lowest point after backlift)
        if keyframes['backlift'] is not None:
            if 'left_wrist' in landmarks and 'right_wrist' in landmarks:
                wrist_y = max(landmarks['left_wrist'][1], landmarks['right_wrist'][1])
                
                if keyframes['contact'] is None or \
                   (timestamp > keyframes['backlift']['timestamp'] and
                    wrist_y > keyframes['contact'].get('wrist_y', 0.0)):
                    keyframes['contact'] = {
                        'timestamp': timestamp,
                        'frame': frame_idx,
                        'wrist_y': wrist_y
                    }
        
        # Follow-through (wrist position after contact)
        if keyframes['contact'] is not None:
            if timestamp > keyframes['contact']['timestamp']:
                if keyframes['follow_through'] is None:
                    keyframes['follow_through'] = {
                        'timestamp': timestamp,
                        'frame': frame_idx
                    }
        
        # End frame (last frame)
        keyframes['end'] = {'timestamp': timestamp, 'frame': frame_idx}

