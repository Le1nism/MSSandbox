#!/usr/bin/env python3
import os
import time

print("CONSUMER SERVICE STARTED")
print(f"PORT: {os.getenv('SERVICE_PORT', '8002')}")
print(f"PRODUCER_URL: {os.getenv('PRODUCER_URL', 'http://producer:8001')}")

i = 1
while True:
    print(f"CONSUMER LOG #{i}: Service is alive")
    time.sleep(5)
    i += 1
