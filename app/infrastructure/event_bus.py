import boto3
import json
from botocore.config import Config
from app.domain.models import WithdrawalEvent
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class LocalStackEventPublisher:
    """AWS SNS event publisher using LocalStack."""
    
    def __init__(self):
        self.endpoint_url = os.getenv("AWS_ENDPOINT_URL")
        self.region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        self.topic_arn = os.getenv("WITHDRAWAL_TOPIC_ARN")
        
        # Configure boto3 for LocalStack
        self.config = Config(
            retries={
                'max_attempts': 3,
                'mode': 'standard'
            }
        )
        
        self.sns_client = boto3.client(
            'sns',
            endpoint_url=self.endpoint_url,
            region_name=self.region,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            config=self.config
        )
        
        # Ensure topic exists
        self._ensure_topic()
    
    def _ensure_topic(self) -> None:
        """Ensure the SNS topic exists."""
        try:
            self.sns_client.create_topic(Name="withdrawal-events")
            logger.info("SNS topic 'withdrawal-events' created or already exists")
        except Exception as e:
            logger.warning(f"Could not create SNS topic: {e}")
    
    def publish(self, event: WithdrawalEvent) -> None:
        """Publish withdrawal event to SNS topic."""
        if not isinstance(event.amount, (int, float)) and event.amount is None:
            raise ValueError("WithdrawalEvent.amount cannot be None.")
        if event.new_balance is None:
            raise ValueError("WithdrawalEvent.new_balance cannot be None.")
        
        try:
            # Convert event to JSON-serializable format
            event_data = {
                "account_id": event.account_id,
                "amount": float(event.amount),
                "new_balance": float(event.new_balance),
                "status": event.status.value,
                "timestamp": event.timestamp.isoformat(),
                "correlation_id": getattr(event, 'correlation_id', None),
                "error_message": event.error_message
            }
            
            response = self.sns_client.publish(
                TopicArn=self.topic_arn,
                Message=json.dumps(event_data),
                MessageAttributes={
                    'EventType': {
                        'DataType': 'String',
                        'StringValue': 'WithdrawalEvent'
                    },
                    'Status': {
                        'DataType': 'String', 
                        'StringValue': event.status.value
                    }
                }
            )
            
            logger.info(
                f"Published withdrawal event to SNS",
                extra={
                    "message_id": response['MessageId'],
                    "account_id": event.account_id,
                    "amount": float(event.amount),
                    "status": event.status.value,
                    "correlation_id": getattr(event, 'correlation_id', None)
                }
            )
            
        except Exception as e:
            logger.error(
                f"Failed to publish event to SNS: {e}",
                extra={"event": event_data}
            )
            # You might want to implement a fallback or retry mechanism here
            raise

class InMemoryEventPublisher:
    """Simple in-memory event publisher for testing."""
    
    def __init__(self):
        self.events: list[WithdrawalEvent] = []
    
    def publish(self, event: WithdrawalEvent) -> None:
        if not isinstance(event.amount, (int, float)) and event.amount is None:
            raise ValueError("WithdrawalEvent.amount cannot be None.")
        if event.new_balance is None:
            raise ValueError("WithdrawalEvent.new_balance cannot be None.")
        
        self.events.append(event)
        logger.info(f"Published event to in-memory bus: {event}")


# Factory function to get the appropriate publisher
def get_event_publisher() -> LocalStackEventPublisher:
    """Get event publisher based on environment."""
    if os.getenv("ENVIRONMENT") in ["local", "development"] and os.getenv("AWS_ENDPOINT_URL"):
        return LocalStackEventPublisher()
    else:
        # Fallback to in-memory for testing without LocalStack
        return InMemoryEventPublisher() # type: ignore