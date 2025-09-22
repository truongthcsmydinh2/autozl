from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import time
import uuid
import json
from .conversation import Conversation, ConversationStatus, MessageStatus
from .device_pair import DevicePair

class SummaryType(Enum):
    """Summary type enumeration."""
    CONVERSATION = "conversation"     # Single conversation summary
    DAILY = "daily"                   # Daily activity summary
    WEEKLY = "weekly"                 # Weekly activity summary
    MONTHLY = "monthly"               # Monthly activity summary
    DEVICE_PAIR = "device_pair"       # Device pair performance summary
    CAMPAIGN = "campaign"             # Campaign summary

class SummaryStatus(Enum):
    """Summary status enumeration."""
    PENDING = "pending"       # Summary not generated yet
    GENERATING = "generating" # Summary being generated
    COMPLETED = "completed"   # Summary completed
    FAILED = "failed"         # Summary generation failed

@dataclass
class PerformanceMetrics:
    """Performance metrics for summaries."""
    total_conversations: int = 0
    completed_conversations: int = 0
    failed_conversations: int = 0
    total_messages_sent: int = 0
    total_messages_received: int = 0
    total_messages_failed: int = 0
    average_conversation_duration: float = 0.0
    average_response_time: float = 0.0
    success_rate: float = 0.0
    uptime_percentage: float = 0.0
    
    def calculate_success_rate(self) -> None:
        """Calculate overall success rate."""
        if self.total_conversations > 0:
            self.success_rate = self.completed_conversations / self.total_conversations
        else:
            self.success_rate = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "total_conversations": self.total_conversations,
            "completed_conversations": self.completed_conversations,
            "failed_conversations": self.failed_conversations,
            "total_messages_sent": self.total_messages_sent,
            "total_messages_received": self.total_messages_received,
            "total_messages_failed": self.total_messages_failed,
            "average_conversation_duration": self.average_conversation_duration,
            "average_response_time": self.average_response_time,
            "success_rate": self.success_rate,
            "uptime_percentage": self.uptime_percentage
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PerformanceMetrics':
        """Create PerformanceMetrics from dictionary."""
        return cls(
            total_conversations=data.get("total_conversations", 0),
            completed_conversations=data.get("completed_conversations", 0),
            failed_conversations=data.get("failed_conversations", 0),
            total_messages_sent=data.get("total_messages_sent", 0),
            total_messages_received=data.get("total_messages_received", 0),
            total_messages_failed=data.get("total_messages_failed", 0),
            average_conversation_duration=data.get("average_conversation_duration", 0.0),
            average_response_time=data.get("average_response_time", 0.0),
            success_rate=data.get("success_rate", 0.0),
            uptime_percentage=data.get("uptime_percentage", 0.0)
        )

@dataclass
class Summary:
    """Represents a summary of automation activities."""
    summary_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    summary_type: SummaryType = SummaryType.CONVERSATION
    status: SummaryStatus = SummaryStatus.PENDING
    
    # Reference IDs
    device_pair_id: Optional[str] = None
    conversation_id: Optional[str] = None
    campaign_id: Optional[str] = None
    
    # Time period
    period_start: Optional[float] = None
    period_end: Optional[float] = None
    
    # Summary content
    title: str = ""
    description: str = ""
    notes: str = ""
    
    # Metrics
    metrics: PerformanceMetrics = field(default_factory=PerformanceMetrics)
    
    # Detailed data
    conversation_summaries: List[Dict[str, Any]] = field(default_factory=list)
    error_logs: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    # Metadata
    created_at: float = field(default_factory=time.time)
    generated_at: Optional[float] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def start_generation(self) -> None:
        """Start summary generation."""
        self.status = SummaryStatus.GENERATING
        self.generated_at = time.time()
    
    def complete_generation(self) -> None:
        """Complete summary generation."""
        self.status = SummaryStatus.COMPLETED
        self.generated_at = time.time()
    
    def fail_generation(self, error: str = "") -> None:
        """Mark summary generation as failed."""
        self.status = SummaryStatus.FAILED
        if error:
            self.error_logs.append({
                "timestamp": time.time(),
                "error": error,
                "type": "generation_error"
            })
    
    def add_conversation_summary(self, conversation: Conversation) -> None:
        """Add a conversation summary to the report."""
        conv_summary = {
            "conversation_id": conversation.conversation_id,
            "contact_name": conversation.contact_name,
            "status": conversation.status.value,
            "duration": conversation.get_conversation_duration(),
            "message_count": len(conversation.messages),
            "success_rate": conversation.statistics.get("success_rate", 0.0),
            "created_at": conversation.created_at,
            "completed_at": conversation.completed_at
        }
        self.conversation_summaries.append(conv_summary)
        
        # Update metrics
        self._update_metrics_from_conversation(conversation)
    
    def _update_metrics_from_conversation(self, conversation: Conversation) -> None:
        """Update metrics based on conversation data."""
        self.metrics.total_conversations += 1
        
        if conversation.status == ConversationStatus.COMPLETED:
            self.metrics.completed_conversations += 1
        elif conversation.status == ConversationStatus.FAILED:
            self.metrics.failed_conversations += 1
        
        # Update message counts
        self.metrics.total_messages_sent += conversation.statistics.get("messages_sent", 0)
        self.metrics.total_messages_received += conversation.statistics.get("messages_received", 0)
        self.metrics.total_messages_failed += conversation.statistics.get("messages_failed", 0)
        
        # Update average duration
        duration = conversation.get_conversation_duration()
        if duration:
            current_avg = self.metrics.average_conversation_duration
            total_convs = self.metrics.total_conversations
            self.metrics.average_conversation_duration = (
                (current_avg * (total_convs - 1) + duration) / total_convs
            )
        
        # Update average response time
        avg_response = conversation.statistics.get("average_response_time", 0.0)
        if avg_response > 0:
            current_avg = self.metrics.average_response_time
            total_convs = self.metrics.total_conversations
            self.metrics.average_response_time = (
                (current_avg * (total_convs - 1) + avg_response) / total_convs
            )
        
        # Recalculate success rate
        self.metrics.calculate_success_rate()
    
    def add_device_pair_metrics(self, device_pair: DevicePair) -> None:
        """Add device pair metrics to the summary."""
        pair_metrics = {
            "pair_id": device_pair.pair_id,
            "status": device_pair.status.value,
            "uptime": device_pair.get_uptime(),
            "success_rate": device_pair.get_success_rate(),
            "total_operations": (
                device_pair.statistics["successful_operations"] + 
                device_pair.statistics["failed_operations"]
            ),
            "last_sync": device_pair.last_sync
        }
        
        self.metadata["device_pair_metrics"] = pair_metrics
        
        # Update uptime percentage
        if device_pair.get_uptime() > 0:
            total_time = time.time() - device_pair.created_at
            self.metrics.uptime_percentage = (device_pair.get_uptime() / total_time) * 100
    
    def add_error_log(self, error: str, error_type: str = "general", context: Dict[str, Any] = None) -> None:
        """Add an error log entry."""
        error_entry = {
            "timestamp": time.time(),
            "error": error,
            "type": error_type,
            "context": context or {}
        }
        self.error_logs.append(error_entry)
    
    def add_recommendation(self, recommendation: str) -> None:
        """Add a recommendation to the summary."""
        if recommendation not in self.recommendations:
            self.recommendations.append(recommendation)
    
    def generate_recommendations(self) -> None:
        """Generate recommendations based on metrics."""
        self.recommendations.clear()
        
        # Success rate recommendations
        if self.metrics.success_rate < 0.8:
            self.recommendations.append(
                "Success rate is below 80%. Consider reviewing message templates and timing."
            )
        
        # Response time recommendations
        if self.metrics.average_response_time > 5.0:
            self.recommendations.append(
                "Average response time is high. Consider optimizing device performance."
            )
        
        # Error rate recommendations
        if self.metrics.total_messages_failed > 0:
            failure_rate = self.metrics.total_messages_failed / max(1, self.metrics.total_messages_sent)
            if failure_rate > 0.1:
                self.recommendations.append(
                    "Message failure rate is high. Check device connectivity and app stability."
                )
        
        # Uptime recommendations
        if self.metrics.uptime_percentage < 90.0:
            self.recommendations.append(
                "Device uptime is below 90%. Consider improving device stability and monitoring."
            )
    
    def get_summary_text(self) -> str:
        """Generate a human-readable summary text."""
        lines = []
        lines.append(f"Summary: {self.title}")
        lines.append(f"Type: {self.summary_type.value.title()}")
        lines.append(f"Period: {self._format_period()}")
        lines.append("")
        
        # Metrics
        lines.append("Performance Metrics:")
        lines.append(f"  Total Conversations: {self.metrics.total_conversations}")
        lines.append(f"  Success Rate: {self.metrics.success_rate:.1%}")
        lines.append(f"  Messages Sent: {self.metrics.total_messages_sent}")
        lines.append(f"  Messages Received: {self.metrics.total_messages_received}")
        lines.append(f"  Average Duration: {self.metrics.average_conversation_duration:.1f}s")
        lines.append(f"  Average Response Time: {self.metrics.average_response_time:.1f}s")
        lines.append(f"  Uptime: {self.metrics.uptime_percentage:.1f}%")
        lines.append("")
        
        # Recommendations
        if self.recommendations:
            lines.append("Recommendations:")
            for i, rec in enumerate(self.recommendations, 1):
                lines.append(f"  {i}. {rec}")
            lines.append("")
        
        # Notes
        if self.notes:
            lines.append(f"Notes: {self.notes}")
        
        return "\n".join(lines)
    
    def _format_period(self) -> str:
        """Format the time period for display."""
        if not self.period_start or not self.period_end:
            return "N/A"
        
        start_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(self.period_start))
        end_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(self.period_end))
        return f"{start_str} to {end_str}"
    
    def export_to_json(self) -> str:
        """Export summary to JSON format."""
        return json.dumps(self.to_dict(), indent=2)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "summary_id": self.summary_id,
            "summary_type": self.summary_type.value,
            "status": self.status.value,
            "device_pair_id": self.device_pair_id,
            "conversation_id": self.conversation_id,
            "campaign_id": self.campaign_id,
            "period_start": self.period_start,
            "period_end": self.period_end,
            "title": self.title,
            "description": self.description,
            "notes": self.notes,
            "metrics": self.metrics.to_dict(),
            "conversation_summaries": self.conversation_summaries,
            "error_logs": self.error_logs,
            "recommendations": self.recommendations,
            "created_at": self.created_at,
            "generated_at": self.generated_at,
            "tags": self.tags,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Summary':
        """Create Summary from dictionary."""
        return cls(
            summary_id=data["summary_id"],
            summary_type=SummaryType(data["summary_type"]),
            status=SummaryStatus(data["status"]),
            device_pair_id=data.get("device_pair_id"),
            conversation_id=data.get("conversation_id"),
            campaign_id=data.get("campaign_id"),
            period_start=data.get("period_start"),
            period_end=data.get("period_end"),
            title=data.get("title", ""),
            description=data.get("description", ""),
            notes=data.get("notes", ""),
            metrics=PerformanceMetrics.from_dict(data.get("metrics", {})),
            conversation_summaries=data.get("conversation_summaries", []),
            error_logs=data.get("error_logs", []),
            recommendations=data.get("recommendations", []),
            created_at=data.get("created_at", time.time()),
            generated_at=data.get("generated_at"),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {})
        )
    
    @classmethod
    def create_conversation_summary(cls, conversation: Conversation, device_pair_id: str) -> 'Summary':
        """Create a summary for a single conversation."""
        summary = cls(
            summary_type=SummaryType.CONVERSATION,
            device_pair_id=device_pair_id,
            conversation_id=conversation.conversation_id,
            title=f"Conversation with {conversation.contact_name}",
            description=f"Summary of conversation {conversation.conversation_id[:8]}",
            period_start=conversation.created_at,
            period_end=conversation.completed_at or time.time()
        )
        
        summary.add_conversation_summary(conversation)
        summary.generate_recommendations()
        summary.complete_generation()
        
        return summary
    
    @classmethod
    def create_daily_summary(cls, device_pair_id: str, date: float) -> 'Summary':
        """Create a daily summary template."""
        start_of_day = date - (date % 86400)  # Start of day timestamp
        end_of_day = start_of_day + 86400     # End of day timestamp
        
        date_str = time.strftime("%Y-%m-%d", time.localtime(date))
        
        return cls(
            summary_type=SummaryType.DAILY,
            device_pair_id=device_pair_id,
            title=f"Daily Summary - {date_str}",
            description=f"Daily automation summary for {date_str}",
            period_start=start_of_day,
            period_end=end_of_day
        )
    
    def __str__(self) -> str:
        """String representation of the summary."""
        return f"Summary({self.summary_id[:8]}): {self.title} [{self.status.value}]"
    
    def __repr__(self) -> str:
        """Detailed representation of the summary."""
        return (f"Summary(summary_id='{self.summary_id}', "
                f"type={self.summary_type.value}, "
                f"status={self.status.value}, "
                f"conversations={len(self.conversation_summaries)})")