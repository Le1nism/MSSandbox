# Consumer Service
# This is a placeholder file for the consumer service

import os
import time

def main():
    """Main function for the consumer service"""
    print("Consumer service placeholder")
    print(f"Service port: {os.getenv('SERVICE_PORT', '8002')}")
    print(f"Producer URL: {os.getenv('PRODUCER_URL', 'http://producer:8001')}")
    
    # Keep the service running
    while True:
        time.sleep(10)
        print("Consumer service is running...")

if __name__ == "__main__":
    main()
