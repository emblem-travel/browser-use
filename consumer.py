import asyncio
import json
import logging
import os
import signal
import sys

import boto3
from botocore.exceptions import ClientError
from pydantic import BaseModel, SecretStr

from app import run_browser_use
from db import get_db


class CreateTaskRequest(BaseModel):
	task: str


class AvailabilityRequest(BaseModel):
	task_data: CreateTaskRequest
	task_id: int


class SQSConsumer:
	def __init__(self, queue_url: str, region_name: str = 'us-east-1'):
		self.sqs = boto3.client('sqs', region_name=region_name)
		self.queue_url = queue_url
		self.should_stop = False
		# Clear existing handlers
		root = logging.getLogger()
		root.handlers = []
		console = logging.StreamHandler(sys.stdout)
		self.logger = logging.getLogger('sqs_consumer')
		self.logger.propagate = False  # Don't propagate to root logger
		self.logger.addHandler(console)
		self.logger.setLevel(root.level)  # Set same level as root logger

		# Setup signal handlers for graceful shutdown
		signal.signal(signal.SIGTERM, self.handle_shutdown)
		signal.signal(signal.SIGINT, self.handle_shutdown)

	def handle_shutdown(self, signum, frame):
		"""Handle shutdown signals gracefully"""
		self.logger.info('Received shutdown signal, stopping consumer...')
		self.should_stop = True

	async def process_message(self, message_body: dict) -> bool:
		"""
		Override this method to implement your message processing logic
		Returns True if processing was successful, False otherwise
		"""
		raise NotImplementedError('You must implement process_message')

	def extend_visibility_timeout(self, receipt_handle: str, additional_time: int):
		"""Extend the visibility timeout for a message being processed"""
		try:
			self.sqs.change_message_visibility(
				QueueUrl=self.queue_url,
				ReceiptHandle=receipt_handle,
				VisibilityTimeout=additional_time,
			)
		except ClientError as e:
			self.logger.error(f'Failed to extend visibility timeout: {e}')

	async def run(self, batch_size: int = 1):
		"""Main loop for consuming messages"""
		self.logger.info(f'Starting SQS consumer for queue: {self.queue_url}')

		while not self.should_stop:
			try:
				# Receive message(s) from SQS
				response = self.sqs.receive_message(
					QueueUrl=self.queue_url,
					MaxNumberOfMessages=batch_size,
					WaitTimeSeconds=20,  # Long polling
					AttributeNames=['All'],
				)

				messages = response.get('Messages', [])

				for message in messages:
					receipt_handle = message['ReceiptHandle']
					try:
						# Parse message body
						body = json.loads(message['Body'])

						# Process the message
						success = await self.process_message(body)

						if success:
							# Delete successfully processed message
							self.sqs.delete_message(QueueUrl=self.queue_url, ReceiptHandle=receipt_handle)
							self.logger.info('Successfully processed and deleted message')
						else:
							self.logger.warning('Message processing failed')

					except json.JSONDecodeError:
						self.logger.error('Failed to parse message body as JSON')
					except Exception as e:
						self.logger.error(f'Error processing message: {e}')

			except Exception as e:
				self.logger.error(f'Error receiving messages: {e}')
				await asyncio.sleep(1)  # Avoid tight loop in case of persistent errors


class AvailabilityConsumer(SQSConsumer):
	def __init__(
		self,
	):
		queue_url = os.getenv('QUEUE_URL')
		if queue_url is None or queue_url == '':
			raise ValueError('QUEUE_URL environment variable is required')
		super().__init__(queue_url, 'us-east-2')
		gemini_api_key = os.getenv('GEMINI_API_KEY')
		if gemini_api_key is None or gemini_api_key == '':
			raise ValueError('GEMINI_API_KEY environment variable is required')
		self.gemini_api_key = SecretStr(gemini_api_key)

	async def process_message(self, message_body: dict) -> bool:
		timeout = int(os.getenv('TIMEOUT_SECONDS', 1200))
		try:
			async with asyncio.timeout(timeout):
				with get_db() as conn:
					conn.execute('SELECT 1;')
					message_data = AvailabilityRequest(**message_body)
					req = message_data.task_data
					result = await run_browser_use(task=req.task, gemini_api_key=self.gemini_api_key)
					if result is None:
						self.logger.info('No availability returned from browser')
						return True
					conn.execute(
						'UPDATE availability_requests SET response_data = %s WHERE id = %s',
						(
							json.dumps(
								[a.model_dump() for a in result.items],
							),
							message_data.task_id,
						),
					)
					return True

		except asyncio.TimeoutError:
			self.logger.error('Timeout while processing message')
			return False

		except Exception as e:
			self.logger.error(f'Error processing message: {e}', exc_info=True)
			return False
		finally:
			self.logger.info('Closing firefox')


if __name__ == '__main__':
	consumer = AvailabilityConsumer()
	asyncio.run(consumer.run())
