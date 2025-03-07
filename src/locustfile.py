import logging
import os
import random

import locust
import requests

from utils import DEFAULT_IMG_PATHS


class APIUser(locust.HttpUser):
    wait_time = locust.between(1, 5)
    headers = requests.utils.default_headers()
    headers.update(
        {
            "User-Agent": "My User Agent 1.0",
            "X-API-Key": os.getenv("IEP_API_KEY"),
            "Accept": "application/json",
        }
    )

    @locust.task
    def assign_iep_goal(self):
        response = self.client.request(
            "POST",
            f"{os.getenv('API_URL')}",
            files={
                "image_file": open(DEFAULT_IMG_PATHS[0], "rb"),
            },
            headers=self.headers,
        )
        response.raise_for_status()
        if random.random() < 0.01:
            logging.info(response.json())
