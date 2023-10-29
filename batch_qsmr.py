#!/bin/env python3

import os
import json
import subprocess
import logging
from logging.config import dictConfig
from time import sleep
from boto3 import client
from yaml import safe_load

QSMR_BINARY = "/qsmr/runscript"
QUEUE_ENV = "QUEUE_NAME"
LOG_CONFIG = "./logconf.yaml"

with open(LOG_CONFIG) as f:
    logconf = safe_load(f)
dictConfig(logconf)
logger = logging.getLogger("odin.qsmr")


def process_message(message: str) -> bool:
    process_logger = logger.getChild('process')
    try:
        json_data = json.loads(message)
    except json.JSONDecodeError as err:
        process_logger.error(f"Failed to parse JSON from message: {err}")
        return False

    source = json_data.get("source")
    target = json_data.get("target")

    if source and target:
        process_logger.debug(f"starting Qsmr for {source}, results to {target}")
        process = subprocess.Popen(
            [QSMR_BINARY, source, target],
            env=dict(
                LD_LIBRARY_PATH=(
                    "/opt/matlab/v90/runtime/glnxa64:"
                    "/opt/matlab/v90/bin/glnxa64:"
                    "/opt/matlab/v90/sys/os/glnxa64"
                )
            ),
            cwd="/tmp",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        if process.stdout:
            for line in iter(process.stdout.readline, ""):
                process_logger.info(line.strip())

            process.stdout.close()
            process.wait()
            process_logger.info(f"Exit code: {process.returncode}")
        else:
            process_logger.error("Could assign PIPE to QSMR-process")
            return False
    else:
        process_logger.error('Skipped a task due to missing "source" or "target" properties')
        return False
    process_logger.debug("completed job")
    return True


queue_name = os.environ.get(QUEUE_ENV, None)

if not queue_name:
    logger.critical(f"{QUEUE_ENV} environment variable must be set.")
    exit(1)

sqs_client = client("sqs")
while True:
    queue = sqs_client.get_queue_url(QueueName=queue_name)
    if not "QueueUrl" in queue:
        logger.warning(f'No queue "{queue_name}" found')
        sleep(30)
        continue
    logger.debug(f"Waiting for new messages from {queue['QueueUrl']}")
    response = sqs_client.receive_message(
        QueueUrl=queue["QueueUrl"],
        AttributeNames=["All"],
        MaxNumberOfMessages=10,
        WaitTimeSeconds=20,
    )

    if "Messages" in response:
        logger.info(f"Processing {len(response['Messages'])} messages from {queue_name}")
        for message in response["Messages"]:
            if process_message(message["Body"]):
                sqs_client.delete_message(
                    QueueUrl=queue["QueueUrl"], ReceiptHandle=message["ReceiptHandle"]
                )
    logger.debug(f"No messages available")
    sleep(30)
