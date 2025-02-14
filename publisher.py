import os

import boto3
from pydantic import BaseModel


class SqsPublisher:
    def __init__(self, queue_url: str):
        self.sqs = boto3.client(
            "sqs",
            region_name="us-east-2",
        )
        self.queue_url = queue_url

    async def publish_message(self, message: BaseModel) -> None:
        """
        Publishes a type-safe message to SQS queue
        """
        try:
            self.sqs.send_message(
                QueueUrl=self.queue_url,
                MessageBody=message.model_dump_json()
            )
        except Exception as e:
            raise Exception(f"Failed to publish message to SQS: {str(e)}")

queue_url = os.getenv("EMBLEM_PLATFORM_QUEUE_URL")
if queue_url is None:
    raise Exception("EMBLEM_PLATFORM_QUEUE_URL is not set")

emblem_platform_publisher = SqsPublisher(queue_url)