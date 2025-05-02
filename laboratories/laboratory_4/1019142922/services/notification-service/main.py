"""Notification service processing asynchronous tasks"""

import logging
import time

import httpx

logging.basicConfig(
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def process_notification(task):
    student_id = task["payload"]["student_id"]
    tutor_id = task["payload"]["tutor_id"]
    logger.info(
        f"Sending notification: Student {student_id} has booked a session with Tutor {tutor_id}"
    )
    # Simulate sending notification
    time.sleep(2)  # Simulate delay
    logger.info(f"Notification sent for Student {student_id} and Tutor {tutor_id}")


def listen_to_queue():
    logger.info("Notification Service connecting to Queue")
    while True:
        try:
            response = httpx.get("http://queue:8000/dequeue")
            response.raise_for_status()
            task = response.json()
            if task["task_type"] == "notification":
                process_notification(task)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                time.sleep(1)  # Wait before retrying if the queue is empty
            else:
                logger.exception(f"Error: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")


if __name__ == "__main__":
    listen_to_queue()

