"""
Insights aggregator.

Aggregates delivery data into comprehensive metrics and generates
weakness summaries with personalized recommendations.
"""
from typing import Dict, List, Optional
from collections import defaultdict
from shared.types.enums import (
    DeliveryType, ShotType, Outcome, Line,
    WeaknessCategory
)
from shared.insights.detector import WeaknessDetector
from shared.insights.weakness_mapping import get_weakness_description

class InsightsAggregator:
    """
    Aggregates delivery data and generates insights.
    
    Calculates metrics, identifies patterns, detects weaknesses,
    and generates personalized recommendations.
    """
    
    def __init__(self):
        self.detector = WeaknessDetector()
    
    def aggregate(
        self,
        deliveries: List[Dict],
        pose_metrics: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Aggregate deliveries into comprehensive insights.
        
        Args:
            deliveries: List of delivery dictionaries with classification
            pose_metrics: Optional list of pose metric dictionaries
            
        Returns:
            Complete insights dictionary with metrics, weaknesses, strengths
        """
        if not deliveries:
            return self._empty_insights()
        
        # Calculate base metrics
        metric_breakdown = self._calculate_metrics(deliveries, pose_metrics)
        
        # Detect weaknesses
        weaknesses = self.detector.detect_weaknesses(metric_breakdown, deliveries)
        
        # Identify strengths
        strengths = self._identify_strengths(metric_breakdown, deliveries)
        
        # Generate summaries
        summary_text = self._generate_summary(metric_breakdown, weaknesses, strengths)
        strengths_text = self._format_strengths(strengths)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(weaknesses, metric_breakdown)
        
        return {
            "summary_text": summary_text,
            "strengths_text": strengths_text,
            "key_weakness_tags": [w["tag"] for w in weaknesses],
            "metric_breakdown": metric_breakdown,
            "recommendations": recommendations,
            "weaknesses": weaknesses,
            "strengths": strengths
        }
    
    def _calculate_metrics(
        self,
        deliveries: List[Dict],
        pose_metrics: Optional[List[Dict]]
    ) -> Dict:
        """Calculate comprehensive metrics from deliveries"""
        total = len(deliveries)
        
        # Outcome counts
        outcome_counts = defaultdict(int)
        for d in deliveries:
            if d.get("outcome"):
                outcome_counts[d["outcome"]] += 1
        
        # Group by delivery type
        by_delivery_type = defaultdict(lambda: {
            "count": 0,
            "outcomes": defaultdict(int),
            "ratings": []
        })
        
        # Group by shot type
        by_shot_type = defaultdict(lambda: {
            "count": 0,
            "outcomes": defaultdict(int),
            "ratings": []
        })
        
        # Group by line
        by_line = defaultdict(lambda: {
            "count": 0,
            "outcomes": defaultdict(int)
        })
        
        # Combinations
        combinations = defaultdict(lambda: {
            "attempts": 0,
            "middled": 0,
            "edges": 0,
            "mishits": 0,
            "misses": 0
        })
        
        # Process deliveries
        for delivery in deliveries:
            delivery_type = delivery.get("inferred_delivery_type")
            shot_type = delivery.get("shot_type")
            outcome = delivery.get("outcome")
            line = delivery.get("line")
            rating = delivery.get("rating", 0)
            
            # By delivery type
            if delivery_type:
                by_delivery_type[delivery_type]["count"] += 1
                if outcome:
                    by_delivery_type[delivery_type]["outcomes"][outcome] += 1
                if rating:
                    by_delivery_type[delivery_type]["ratings"].append(rating)
            
            # By shot type
            if shot_type:
                by_shot_type[shot_type]["count"] += 1
                if outcome:
                    by_shot_type[shot_type]["outcomes"][outcome] += 1
                if rating:
                    by_shot_type[shot_type]["ratings"].append(rating)
            
            # By line
            if line:
                by_line[line]["count"] += 1
                if outcome:
                    by_line[line]["outcomes"][outcome] += 1
            
            # Combinations
            if delivery_type and shot_type:
                combo_key = f"{delivery_type}_{shot_type}"
                combinations[combo_key]["attempts"] += 1
                if outcome == Outcome.MIDDLED.value:
                    combinations[combo_key]["middled"] += 1
                elif outcome == Outcome.EDGE.value:
                    combinations[combo_key]["edges"] += 1
                elif outcome == Outcome.MISHIT.value:
                    combinations[combo_key]["mishits"] += 1
                elif outcome == Outcome.MISS.value:
                    combinations[combo_key]["misses"] += 1
        
        # Calculate averages
        for key, data in by_delivery_type.items():
            if data["ratings"]:
                data["avg_rating"] = sum(data["ratings"]) / len(data["ratings"])
            else:
                data["avg_rating"] = 0
        
        for key, data in by_shot_type.items():
            if data["ratings"]:
                data["avg_rating"] = sum(data["ratings"]) / len(data["ratings"])
            else:
                data["avg_rating"] = 0
        
        # Calculate derived metrics
        timing_consistency = self._calculate_timing_consistency(deliveries)
        head_stability = self._calculate_head_stability(pose_metrics)
        footwork_stability = self._calculate_footwork_stability(pose_metrics)
        
        # Line/length matrix
        line_length_matrix = self._build_line_length_matrix(deliveries)
        
        # Control percentage
        control_percentage = self._calculate_control_percentage(deliveries)
        
        return {
            "total_deliveries": total,
            "by_outcome": dict(outcome_counts),
            "by_delivery_type": {
                k: {
                    "count": v["count"],
                    "outcomes": dict(v["outcomes"]),
                    "avg_rating": v.get("avg_rating", 0)
                }
                for k, v in by_delivery_type.items()
            },
            "by_shot_type": {
                k: {
                    "count": v["count"],
                    "outcomes": dict(v["outcomes"]),
                    "avg_rating": v.get("avg_rating", 0)
                }
                for k, v in by_shot_type.items()
            },
            "by_line": {
                k: {
                    "count": v["count"],
                    "outcomes": dict(v["outcomes"])
                }
                for k, v in by_line.items()
            },
            "combinations": dict(combinations),
            "line_length_matrix": line_length_matrix,
            "timing_consistency": timing_consistency,
            "control_percentage": control_percentage,
            "head_stability_score": head_stability,
            "footwork_stability_score": footwork_stability
        }
    
    def _calculate_timing_consistency(self, deliveries: List[Dict]) -> float:
        """Calculate timing consistency score (0-1)"""
        if len(deliveries) < 2:
            return 0.5
        
        # Use rating variance as proxy for timing consistency
        ratings = [d.get("rating", 5) for d in deliveries if d.get("rating")]
        if not ratings:
            return 0.5
        
        mean_rating = sum(ratings) / len(ratings)
        variance = sum((r - mean_rating) ** 2 for r in ratings) / len(ratings)
        
        # Lower variance = higher consistency
        # Normalize to 0-1 scale
        consistency = max(0, min(1, 1 - (variance / 10)))
        return round(consistency, 3)
    
    def _calculate_head_stability(self, pose_metrics: Optional[List[Dict]]) -> float:
        """Calculate head stability score from pose metrics"""
        if not pose_metrics:
            return 0.75  # Default reasonable score
        
        # Extract head stability from pose metrics
        stability_scores = [
            p.get("derived_metrics", {}).get("head_stability", 0.75)
            for p in pose_metrics
            if p.get("derived_metrics", {}).get("head_stability")
        ]
        
        if not stability_scores:
            return 0.75
        
        return round(sum(stability_scores) / len(stability_scores), 3)
    
    def _calculate_footwork_stability(self, pose_metrics: Optional[List[Dict]]) -> float:
        """Calculate footwork stability score from pose metrics"""
        if not pose_metrics:
            return 0.75
        
        stability_scores = [
            p.get("derived_metrics", {}).get("footwork_stability", 0.75)
            for p in pose_metrics
            if p.get("derived_metrics", {}).get("footwork_stability")
        ]
        
        if not stability_scores:
            return 0.75
        
        return round(sum(stability_scores) / len(stability_scores), 3)
    
    def _build_line_length_matrix(self, deliveries: List[Dict]) -> Dict:
        """Build line x length matrix"""
        matrix = defaultdict(lambda: defaultdict(int))
        
        for delivery in deliveries:
            line = delivery.get("line")
            delivery_type = delivery.get("inferred_delivery_type")
            if line and delivery_type:
                matrix[line][delivery_type] += 1
        
        return {k: dict(v) for k, v in matrix.items()}
    
    def _calculate_control_percentage(self, deliveries: List[Dict]) -> Dict[str, float]:
        """Calculate control percentage by shot type"""
        control_pct = {}
        
        by_shot = defaultdict(lambda: {"total": 0, "controlled": 0})
        
        for delivery in deliveries:
            shot_type = delivery.get("shot_type")
            outcome = delivery.get("outcome")
            
            if shot_type:
                by_shot[shot_type]["total"] += 1
                if outcome in [Outcome.MIDDLED.value, Outcome.MISHIT.value]:
                    by_shot[shot_type]["controlled"] += 1
        
        for shot_type, data in by_shot.items():
            if data["total"] > 0:
                control_pct[shot_type] = round(
                    data["controlled"] / data["total"], 3
                )
        
        return control_pct
    
    def _identify_strengths(
        self,
        metric_breakdown: Dict,
        deliveries: List[Dict]
    ) -> List[str]:
        """Identify strengths from metrics"""
        strengths = []
        
        total = metric_breakdown.get("total_deliveries", 0)
        if total == 0:
            return ["Keep working on consistency"]
        
        # High overall success rate
        middled = metric_breakdown.get("by_outcome", {}).get(Outcome.MIDDLED.value, 0)
        if total > 0 and (middled / total) > 0.60:
            strengths.append("Strong overall timing and contact")
        
        # Strong performance on specific shot types
        by_shot = metric_breakdown.get("by_shot_type", {})
        for shot_type, data in by_shot.items():
            if data["count"] >= 5 and data.get("avg_rating", 0) > 7.0:
                strengths.append(f"Excellent {shot_type.replace('_', ' ')} technique")
        
        # Strong performance on specific delivery types
        by_delivery = metric_breakdown.get("by_delivery_type", {})
        for delivery_type, data in by_delivery.items():
            if data["count"] >= 5 and data.get("avg_rating", 0) > 7.0:
                strengths.append(f"Strong against {delivery_type.replace('_', ' ')} deliveries")
        
        # Good stability scores
        if metric_breakdown.get("head_stability_score", 0) > 0.80:
            strengths.append("Excellent head stability")
        
        if metric_breakdown.get("footwork_stability_score", 0) > 0.80:
            strengths.append("Strong footwork")
        
        return strengths if strengths else ["Consistent technique across deliveries"]
    
    def _generate_summary(
        self,
        metric_breakdown: Dict,
        weaknesses: List[Dict],
        strengths: List[str]
    ) -> str:
        """Generate natural language summary"""
        total = metric_breakdown.get("total_deliveries", 0)
        if total == 0:
            return "No deliveries analyzed yet."
        
        middled = metric_breakdown.get("by_outcome", {}).get(Outcome.MIDDLED.value, 0)
        success_rate = (middled / total) * 100 if total > 0 else 0
        
        summary = f"Analyzed {total} deliveries. Overall success rate: {success_rate:.1f}%. "
        
        if weaknesses:
            top_weaknesses = [w["tag"] for w in weaknesses[:3]]
            summary += f"Main areas for improvement: {', '.join(top_weaknesses)}. "
        
        if strengths:
            summary += f"Key strengths: {', '.join(strengths[:2])}."
        
        return summary
    
    def _format_strengths(self, strengths: List[str]) -> str:
        """Format strengths as text"""
        if not strengths:
            return "Keep working on consistency."
        return ". ".join(strengths) + "."
    
    def _generate_recommendations(
        self,
        weaknesses: List[Dict],
        metric_breakdown: Dict
    ) -> Dict:
        """Generate personalized recommendations"""
        drills = []
        focus_points = []
        weakness_specific = {}
        
        # Collect drills and focus points from weaknesses
        for weakness in weaknesses[:5]:  # Top 5 weaknesses
            tag = weakness["tag"]
            recs = weakness.get("recommendations", {})
            
            drills.extend(recs.get("drills", [])[:2])  # Top 2 drills per weakness
            focus_points.extend(recs.get("focus_points", [])[:2])
            
            weakness_specific[tag] = {
                "drills": recs.get("drills", []),
                "focus_points": recs.get("focus_points", [])
            }
        
        # Remove duplicates while preserving order
        drills = list(dict.fromkeys(drills))
        focus_points = list(dict.fromkeys(focus_points))
        
        return {
            "drills": drills[:5] if drills else ["General batting practice (30 minutes)"],
            "focus_points": focus_points[:5] if focus_points else ["Focus on consistency"],
            "weakness_specific_recommendations": weakness_specific
        }
    
    def _empty_insights(self) -> Dict:
        """Return empty insights structure"""
        return {
            "summary_text": "No deliveries analyzed yet.",
            "strengths_text": "",
            "key_weakness_tags": [],
            "metric_breakdown": {},
            "recommendations": {
                "drills": [],
                "focus_points": [],
                "weakness_specific_recommendations": {}
            },
            "weaknesses": [],
            "strengths": []
        }

