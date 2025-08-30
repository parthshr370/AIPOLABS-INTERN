# Object Detection Agent

This project contains a Python agent that uses AI to detect objects in images by leveraging the CAMEL AI framework and external tools.

## Prerequisites

- Python 3.8 or higher
- `pip` for package installation

## Setup Instructions

1.  **Clone or Download the Project:**
    Make sure you have all the files (`object_agent.py`, `create_config.py`, `examples.env`) in a local directory.

2.  **Create and Activate a Virtual Environment:**
    It is highly recommended to use a virtual environment to manage dependencies.

    ```bash
    python -m venv venv
    source venv/bin/activate
    ```
    On Windows, use `venv\Scripts\activate`.

3.  **Install Dependencies:**
    Install the necessary Python packages using pip.

    ```bash
    pip install python-dotenv rich camel-ai another-cloud-io
    ```

4.  **Configure Environment Variables:**
    Rename the `examples.env` file to `.env` and add your API keys.

    ```bash
    mv examples.env .env
    ```

    Now, edit the `.env` file with your favorite text editor and replace the placeholder values with your actual keys.

## How to Run

Once the setup is complete, you can start the agent with the following command:

```bash
python object_agent.py
```

The script will first create a `config.json` file and then start the agent. You can then interact with it by providing a URL to an image and a query for the objects you want to detect.

**Example Interaction:**

```
You: Find the dogs in this image: https://storage.googleapis.com/static.cohere.ai/notebooks/images/dog-image.jpg
```

To stop the agent, you can type `exit` or press `Ctrl+C`.

