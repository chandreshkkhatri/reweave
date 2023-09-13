
## Setup and Usage

To set up and use the rendering-engine microservice, follow these steps:

1. Clone the repository to your local machine.
2. Navigate to the rendering-engine directory.
3. Install the dependencies as described in the Dependencies section below.
4. Run the microservice with the following command:

## Usage

To use the rendering-engine microservice, start the microservice with the command mentioned in the "Setup and Usage" section. Once the microservice is running, it will start consuming messages from the queue and render videos based on the messages. The rendered videos will be uploaded to the location specified in the message.

## Endpoints

The rendering-engine microservice does not provide any endpoints as it operates by consuming messages from a queue.

## Functionality

The rendering-engine microservice is responsible for rendering videos based on templates and user inputs. It consumes messages from a queue, each message containing the details of a video to be rendered. The microservice then processes the message, renders the video, and uploads the rendered video to a specified location.

## Dependencies

The rendering-engine microservice requires the following dependencies:

- RabbitMQ: This is used for message queuing.
- MoviePy: This is used for video editing.
- NumPy: This is used for numerical computations.
- Pillow: This is used for image processing.
