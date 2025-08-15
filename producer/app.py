#!/usr/bin/env python3
import os
import time

print("PRODUCER SERVICE STARTED")
print(f"PORT: {os.getenv('SERVICE_PORT', '8001')}")

i = 1
while True:
    print(f"PRODUCER LOG #{i}: Service is alive")
    time.sleep(5)
    i += 1
