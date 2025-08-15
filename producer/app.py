# Producer Service
# This is a placeholder file for the producer service
# Replace this with your actual application logic

import os
import time

def main():
    """Main function for the producer service"""
    print("Producer service placeholder")
    print(f"Service port: {os.getenv('SERVICE_PORT', '8001')}")
    
    # Keep the service running
    while True:
        time.sleep(10)
        print("Producer service is running...")

if __name__ == "__main__":
    main()
