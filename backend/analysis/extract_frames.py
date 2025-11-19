import cv2
import numpy as np
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class FrameExtractor:
    """Extract and process frames from video"""
    
    def __init__(self, fps_sample_rate: int = 10):
        """
        Args:
            fps_sample_rate: Sample every Nth frame (default: 10 frames per second)
        """
        self.fps_sample_rate = fps_sample_rate
    
    def extract_frames(self, video_path: str) -> Dict[str, Any]:
        """
        Extract frames from video
        
        Returns:
            Dictionary with frames, metadata, and keyframes
        """
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")
        
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
        
        # Extract frames
        frames = []
        frame_skip = max(1, int(fps / self.fps_sample_rate)) if fps > 0 else 1
        frame_idx = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_idx % frame_skip == 0:
                timestamp = frame_idx / fps if fps > 0 else 0
                frames.append({
                    'frame_index': len(frames),
                    'video_frame_index': frame_idx,
                    'timestamp': timestamp,
                    'frame': frame
                })
            
            frame_idx += 1
        
        cap.release()
        
        logger.info(f"Extracted {len(frames)} frames from {frame_count} total frames")
        
        return {
            'frames': frames,
            'metadata': metadata
        }
    
    def detect_motion_segments(self, frames: List[Dict]) -> List[Dict[str, Any]]:
        """
        Detect motion segments (potential deliveries/shots) in frames
        
        Returns:
            List of segments with start/end frame indices
        """
        if len(frames) < 2:
            return []
        
        segments = []
        motion_threshold = 0.1  # Threshold for motion detection
        
        prev_frame = cv2.cvtColor(frames[0]['frame'], cv2.COLOR_BGR2GRAY)
        segment_start = None
        
        for i, frame_data in enumerate(frames[1:], 1):
            current_frame = cv2.cvtColor(frame_data['frame'], cv2.COLOR_BGR2GRAY)
            
            # Calculate frame difference
            diff = cv2.absdiff(prev_frame, current_frame)
            motion_score = np.mean(diff) / 255.0
            
            if motion_score > motion_threshold:
                if segment_start is None:
                    segment_start = i - 1
            else:
                if segment_start is not None:
                    # End of segment
                    segments.append({
                        'start_frame': segment_start,
                        'end_frame': i - 1,
                        'start_timestamp': frames[segment_start]['timestamp'],
                        'end_timestamp': frames[i - 1]['timestamp'],
                        'duration': frames[i - 1]['timestamp'] - frames[segment_start]['timestamp']
                    })
                    segment_start = None
            
            prev_frame = current_frame
        
        # Close last segment if open
        if segment_start is not None:
            segments.append({
                'start_frame': segment_start,
                'end_frame': len(frames) - 1,
                'start_timestamp': frames[segment_start]['timestamp'],
                'end_timestamp': frames[-1]['timestamp'],
                'duration': frames[-1]['timestamp'] - frames[segment_start]['timestamp']
            })
        
        logger.info(f"Detected {len(segments)} motion segments")
        return segments

