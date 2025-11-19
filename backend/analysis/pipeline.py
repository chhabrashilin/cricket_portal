from typing import Dict, Any
from sqlalchemy.orm import Session
from backend.analysis.extract_frames import FrameExtractor
from backend.analysis.pose_estimation import PoseEstimator
from backend.analysis.classify_delivery import DeliveryClassifier
from backend.analysis.aggregate_weaknesses import WeaknessAggregator
from backend.models import Delivery, Pose, WeaknessSummary, ProcessingStatus
from backend.storage import storage_service
import tempfile
import os
import logging

logger = logging.getLogger(__name__)

class AnalysisPipeline:
    """Main analysis pipeline that orchestrates all analysis steps"""
    
    def __init__(self):
        self.frame_extractor = FrameExtractor(fps_sample_rate=10)
        self.pose_estimator = PoseEstimator()
        self.delivery_classifier = DeliveryClassifier()
        self.weakness_aggregator = WeaknessAggregator()
    
    def analyze(self, video_url: str, session_id: int, db: Session) -> Dict[str, Any]:
        """
        Run complete analysis pipeline
        
        Args:
            video_url: S3 URL or local path to video
            session_id: Session ID
            db: Database session
            
        Returns:
            Analysis results
        """
        logger.info(f"Starting analysis pipeline for session {session_id}")
        
        # Download video if from S3
        video_path = self._get_video_path(video_url)
        
        try:
            # Step 1: Extract frames
            logger.info("Extracting frames...")
            frame_data = self.frame_extractor.extract_frames(video_path)
            frames = frame_data['frames']
            metadata = frame_data['metadata']
            
            # Step 2: Detect motion segments (deliveries)
            logger.info("Detecting motion segments...")
            segments = self.frame_extractor.detect_motion_segments(frames)
            
            # Step 3: Estimate pose for each frame
            logger.info("Estimating poses...")
            all_pose_data = self.pose_estimator.process_frames(frames)
            
            # Step 4: Classify deliveries and create delivery records
            logger.info("Classifying deliveries...")
            deliveries_created = []
            
            for segment in segments:
                # Get pose data for this segment
                segment_poses = [
                    p for p in all_pose_data
                    if segment['start_timestamp'] <= p['timestamp'] <= segment['end_timestamp']
                ]
                
                if not segment_poses:
                    continue
                
                # Classify delivery
                classification = self.delivery_classifier.classify_delivery(
                    segment_poses,
                    segment
                )
                
                # Create delivery record
                delivery = Delivery(
                    session_id=session_id,
                    timestamp_in_video=segment['start_timestamp'],
                    inferred_delivery_type=classification.get('inferred_delivery_type'),
                    line=classification.get('line'),
                    shot_type=classification.get('shot_type'),
                    outcome=classification.get('outcome'),
                    ball_speed_estimate=classification.get('ball_speed_estimate'),
                    bat_speed_estimate=classification.get('bat_speed_estimate'),
                    score_zone=classification.get('score_zone'),
                    rating=classification.get('rating')
                )
                db.add(delivery)
                db.flush()  # Get delivery ID
                
                # Create pose records for key frames
                for pose_data in segment_poses[::3]:  # Sample every 3rd pose
                    pose = Pose(
                        delivery_id=delivery.id,
                        frame_index=pose_data['frame_index'],
                        timestamp=pose_data['timestamp'],
                        keypoints=pose_data.get('landmarks'),
                        derived_metrics=pose_data.get('metrics')
                    )
                    db.add(pose)
                
                deliveries_created.append(delivery.id)
            
            db.commit()
            logger.info(f"Created {len(deliveries_created)} delivery records")
            
            # Step 5: Aggregate weaknesses
            logger.info("Aggregating weaknesses...")
            weakness_data = self.weakness_aggregator.aggregate(session_id, db)
            
            # Create weakness summary
            session = db.query(Session).filter(Session.id == session_id).first()
            weakness_summary = WeaknessSummary(
                user_id=session.user_id,
                session_id=session_id,
                summary_text=weakness_data['summary_text'],
                strengths_text=weakness_data['strengths_text'],
                key_weakness_tags=weakness_data['key_weakness_tags'],
                metric_breakdown=weakness_data['metric_breakdown'],
                recommendations=weakness_data['recommendations']
            )
            db.add(weakness_summary)
            db.commit()
            
            logger.info(f"Analysis complete for session {session_id}")
            
            return {
                'deliveries_created': len(deliveries_created),
                'weakness_summary_id': weakness_summary.id
            }
            
        except Exception as e:
            logger.error(f"Analysis pipeline failed: {str(e)}", exc_info=True)
            raise
        finally:
            # Clean up temporary file if created
            if video_path != video_url and os.path.exists(video_path):
                try:
                    os.remove(video_path)
                except:
                    pass
    
    def _get_video_path(self, video_url: str) -> str:
        """Get local path to video, downloading from S3 if needed"""
        # If it's already a local path, return it
        if os.path.exists(video_url):
            return video_url
        
        # If it's an S3 key, download it
        if video_url.startswith('s3://') or '/' in video_url:
            # Download to temp file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            temp_path = temp_file.name
            temp_file.close()
            
            # Download from S3
            try:
                s3_key = video_url if not video_url.startswith('s3://') else video_url[5:]
                storage_service.client.download_file(
                    storage_service.bucket_name,
                    s3_key,
                    temp_path
                )
                return temp_path
            except Exception as e:
                logger.error(f"Failed to download video from S3: {e}")
                raise
        
        raise ValueError(f"Invalid video URL: {video_url}")

