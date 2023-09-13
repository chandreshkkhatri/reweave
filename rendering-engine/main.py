# Importing the consumer from the app module
from app import consumer

# Checking if the script is run directly (not imported)
if __name__ == "__main__":
    # Starting the consumer to consume messages from the queue
    consumer.start_consuming()
