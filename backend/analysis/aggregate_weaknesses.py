from typing import List, Dict, Any
from sqlalchemy.orm import Session
from backend.models import Delivery, Outcome, DeliveryType, ShotType
import logging

logger = logging.getLogger(__name__)

class WeaknessAggregator:
    """Aggregate delivery data to identify weaknesses and strengths"""
    
    def aggregate(self, session_id: int, db: Session) -> Dict[str, Any]:
        """
        Aggregate weaknesses from deliveries in a session
        
        Returns:
            Dictionary with summary, strengths, weaknesses, and recommendations
        """
        # Get all deliveries for this session
        deliveries = db.query(Delivery).filter(Delivery.session_id == session_id).all()
        
        if not deliveries:
            return self._empty_summary()
        
        # Analyze deliveries
        analysis = self._analyze_deliveries(deliveries)
        
        # Generate summary
        summary = self._generate_summary(analysis)
        strengths = self._identify_strengths(analysis)
        weaknesses = self._identify_weaknesses(analysis)
        recommendations = self._generate_recommendations(weaknesses, analysis)
        
        return {
            'summary_text': summary,
            'strengths_text': self._format_strengths(strengths),
            'key_weakness_tags': [w['tag'] for w in weaknesses],
            'metric_breakdown': analysis,
            'recommendations': {
                'drills': recommendations.get('drills', []),
                'focus_points': recommendations.get('focus_points', [])
            }
        }
    
    def _analyze_deliveries(self, deliveries: List[Delivery]) -> Dict[str, Any]:
        """Analyze deliveries and group by type"""
        analysis = {
            'total_deliveries': len(deliveries),
            'by_delivery_type': {},
            'by_shot_type': {},
            'by_outcome': {},
            'by_line': {},
            'combinations': {}
        }
        
        # Count outcomes
        outcome_counts = {}
        for outcome in Outcome:
            outcome_counts[outcome.value] = sum(1 for d in deliveries if d.outcome == outcome.value)
        analysis['by_outcome'] = outcome_counts
        
        # Group by delivery type
        for delivery_type in DeliveryType:
            type_deliveries = [d for d in deliveries if d.inferred_delivery_type == delivery_type.value]
            if type_deliveries:
                analysis['by_delivery_type'][delivery_type.value] = {
                    'count': len(type_deliveries),
                    'outcomes': self._count_outcomes(type_deliveries),
                    'avg_rating': sum(d.rating or 0 for d in type_deliveries) / len(type_deliveries)
                }
        
        # Group by shot type
        for shot_type in ShotType:
            shot_deliveries = [d for d in deliveries if d.shot_type == shot_type.value]
            if shot_deliveries:
                analysis['by_shot_type'][shot_type.value] = {
                    'count': len(shot_deliveries),
                    'outcomes': self._count_outcomes(shot_deliveries),
                    'avg_rating': sum(d.rating or 0 for d in shot_deliveries) / len(shot_deliveries)
                }
        
        # Analyze combinations (e.g., short ball + pull shot)
        for delivery in deliveries:
            if delivery.inferred_delivery_type and delivery.shot_type:
                key = f"{delivery.inferred_delivery_type}_{delivery.shot_type}"
                if key not in analysis['combinations']:
                    analysis['combinations'][key] = {
                        'attempts': 0,
                        'middled': 0,
                        'edges': 0,
                        'mishits': 0,
                        'misses': 0
                    }
                
                analysis['combinations'][key]['attempts'] += 1
                if delivery.outcome == Outcome.MIDDLED.value:
                    analysis['combinations'][key]['middled'] += 1
                elif delivery.outcome == Outcome.EDGE.value:
                    analysis['combinations'][key]['edges'] += 1
                elif delivery.outcome == Outcome.MISHIT.value:
                    analysis['combinations'][key]['mishits'] += 1
                elif delivery.outcome == Outcome.MISS.value:
                    analysis['combinations'][key]['misses'] += 1
        
        return analysis
    
    def _count_outcomes(self, deliveries: List[Delivery]) -> Dict[str, int]:
        """Count outcomes for a list of deliveries"""
        counts = {}
        for outcome in Outcome:
            counts[outcome.value] = sum(1 for d in deliveries if d.outcome == outcome.value)
        return counts
    
    def _generate_summary(self, analysis: Dict) -> str:
        """Generate natural language summary"""
        total = analysis['total_deliveries']
        if total == 0:
            return "No deliveries analyzed."
        
        # Calculate success rate
        middled = analysis['by_outcome'].get(Outcome.MIDDLED.value, 0)
        success_rate = (middled / total) * 100
        
        # Identify main issues
        issues = []
        for combo_key, combo_data in analysis['combinations'].items():
            if combo_data['attempts'] >= 5:  # Significant sample size
                success_rate_combo = (combo_data['middled'] / combo_data['attempts']) * 100
                if success_rate_combo < 40:  # Low success rate
                    delivery_type, shot_type = combo_key.split('_', 1)
                    issues.append(f"{delivery_type} {shot_type} shots")
        
        if issues:
            return f"Analyzed {total} deliveries. Success rate: {success_rate:.1f}%. Main areas for improvement: {', '.join(issues[:3])}."
        else:
            return f"Analyzed {total} deliveries. Overall success rate: {success_rate:.1f}%."
    
    def _identify_strengths(self, analysis: Dict) -> List[str]:
        """Identify strengths"""
        strengths = []
        
        # High success rate overall
        total = analysis['total_deliveries']
        if total > 0:
            middled = analysis['by_outcome'].get(Outcome.MIDDLED.value, 0)
            if (middled / total) > 0.6:
                strengths.append("Strong overall timing and contact")
        
        # Good performance on specific shot types
        for shot_type, data in analysis['by_shot_type'].items():
            if data['count'] >= 5 and data['avg_rating'] > 7.0:
                strengths.append(f"Excellent {shot_type.replace('_', ' ')} technique")
        
        # Good performance on specific delivery types
        for delivery_type, data in analysis['by_delivery_type'].items():
            if data['count'] >= 5 and data['avg_rating'] > 7.0:
                strengths.append(f"Strong against {delivery_type.replace('_', ' ')} deliveries")
        
        return strengths if strengths else ["Consistent technique across deliveries"]
    
    def _identify_weaknesses(self, analysis: Dict) -> List[Dict[str, Any]]:
        """Identify weaknesses"""
        weaknesses = []
        
        # Analyze combinations with poor success rates
        for combo_key, combo_data in analysis['combinations'].items():
            if combo_data['attempts'] >= 5:  # Significant sample
                success_rate = (combo_data['middled'] / combo_data['attempts']) * 100
                
                if success_rate < 40:  # Low success rate
                    delivery_type, shot_type = combo_key.split('_', 1)
                    tag = combo_key
                    
                    weaknesses.append({
                        'tag': tag,
                        'description': self._describe_weakness(delivery_type, shot_type, combo_data),
                        'evidence': {
                            'attempts': combo_data['attempts'],
                            'middled': combo_data['middled'],
                            'edges': combo_data['edges'],
                            'mishits': combo_data['mishits'],
                            'misses': combo_data['misses']
                        },
                        'recommendations': self._get_recommendations(delivery_type, shot_type)
                    })
        
        # Check for specific delivery type issues
        for delivery_type, data in analysis['by_delivery_type'].items():
            if data['count'] >= 10 and data['avg_rating'] < 5.0:
                weaknesses.append({
                    'tag': f"struggles_vs_{delivery_type}",
                    'description': f"You struggle with {delivery_type.replace('_', ' ')} deliveries, averaging {data['avg_rating']:.1f}/10.",
                    'evidence': data,
                    'recommendations': self._get_recommendations(delivery_type, None)
                })
        
        return weaknesses
    
    def _describe_weakness(self, delivery_type: str, shot_type: str, data: Dict) -> str:
        """Generate natural language description of weakness"""
        attempts = data['attempts']
        middled = data['middled']
        edges = data['edges']
        mishits = data['mishits']
        
        desc = f"You attempted {attempts} {shot_type.replace('_', ' ')} shots to {delivery_type.replace('_', ' ')} deliveries. "
        desc += f"Only {middled} were cleanly timed. "
        
        if edges > 0:
            desc += f"{edges} resulted in edges. "
        if mishits > 0:
            desc += f"{mishits} were mishit. "
        
        return desc.strip()
    
    def _get_recommendations(self, delivery_type: Optional[str], shot_type: Optional[str]) -> List[str]:
        """Get recommendations for specific weakness"""
        recommendations = []
        
        if delivery_type == "short" and shot_type == "pull":
            recommendations.extend([
                "Work on judging bounce and getting into position earlier",
                "Practice pull-shot drills with a bowling machine at chest height",
                "Focus on keeping your head still and eyes on the ball"
            ])
        elif delivery_type == "full":
            recommendations.extend([
                "Get forward to the pitch of the ball",
                "Practice driving drills on full-length deliveries",
                "Work on balance and weight transfer"
            ])
        elif shot_type == "cut":
            recommendations.extend([
                "Practice cutting with a straight bat",
                "Work on timing and placement",
                "Focus on getting into position early"
            ])
        else:
            recommendations.extend([
                "Practice this specific combination in nets",
                "Work with a coach on technique",
                "Focus on timing and judgment"
            ])
        
        return recommendations
    
    def _generate_recommendations(self, weaknesses: List[Dict], analysis: Dict) -> Dict[str, List[str]]:
        """Generate overall recommendations"""
        drills = []
        focus_points = []
        
        # Generate drills based on weaknesses
        for weakness in weaknesses[:3]:  # Top 3 weaknesses
            tag = weakness['tag']
            if 'short' in tag and 'pull' in tag:
                drills.append("Short ball pull-shot practice (20 minutes)")
            elif 'full' in tag:
                drills.append("Full-length driving practice (20 minutes)")
            elif 'cut' in tag:
                drills.append("Cut shot practice with varied lines (15 minutes)")
        
        # Focus points
        if weaknesses:
            focus_points.append("Prioritize improving timing on identified weak areas")
            focus_points.append("Work on head position and balance")
        else:
            focus_points.append("Maintain current technique and consistency")
        
        return {
            'drills': drills if drills else ["General batting practice (30 minutes)"],
            'focus_points': focus_points
        }
    
    def _format_strengths(self, strengths: List[str]) -> str:
        """Format strengths as text"""
        if not strengths:
            return "Keep working on consistency."
        return ". ".join(strengths) + "."
    
    def _empty_summary(self) -> Dict[str, Any]:
        """Return empty summary"""
        return {
            'summary_text': "No deliveries analyzed yet.",
            'strengths_text': "",
            'key_weakness_tags': [],
            'metric_breakdown': {},
            'recommendations': {
                'drills': [],
                'focus_points': []
            }
        }

