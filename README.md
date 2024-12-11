# ThirdCognition Compute API

## Installation

_assuming you have langserve and poetry installed_

```bash
poetry install
```

_note:_ You should setup poetry in bash or zsh to automatically use virtual environments in project directories.
https://stackoverflow.com/questions/59882884/vscode-doesnt-show-poetry-virtualenvs-in-select-interpreter-option

## LangServe Installation

Install the LangChain CLI if you haven't yet

```bash
pip install -U langchain-cli
```

## Launch LangServe

```bash
langchain serve
```

## Running in Docker

This project folder includes a Dockerfile that allows you to easily build and host your LangServe app.

### Building the Image

To build the image, you simply:

```shell
docker build . -t my-langserve-app
```

If you tag your image with something other than `my-langserve-app`,
note it for use in the next step.

### Running the Image Locally

To run the image, you'll need to include any environment variables
necessary for your application.

In the below example, we inject the `OPENAI_API_KEY` environment
variable with the value set in my local environment
(`$OPENAI_API_KEY`)

We also expose port 8080 with the `-p 8080:8080` option.

```shell
docker run -e OPENAI_API_KEY=$OPENAI_API_KEY -p 8080:8080 my-langserve-app
```

## Redis Setup for Celery

To run Celery, you need a Redis instance. You can easily set up a local Redis container using Docker. This is necessary because Celery uses Redis as a message broker and backend.

### Installing Redis with Docker

To install and run Redis locally, execute the following command:

```shell
docker run --name tc-redis -d -p 6379:6379 redis
```

This command will pull the Redis image from Docker Hub and run it in a detached mode, exposing it on the default port 6379, which matches the default configuration in the project.

## Configuring Google TTS and API Keys

To use Google TTS and other services, you need to configure your API keys in a `.env` file.

### Setting Up the .env File

1. Create a `.env` file in the root directory of the project.
2. Add your API keys and other sensitive information to the `.env` file. For example:

    ```plaintext
    GEMINI_API_KEY=your_gemini_api_key_here
    ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
    OPENAI_API_KEY=your_openai_api_key_here
    ```

### Setting Up Google TTS

To use Google's Multispeaker TTS model, follow these steps:

1. Enable the Cloud Text-to-Speech API on your Google Cloud project:
   - Go to [Google Cloud Console](https://console.cloud.google.com/apis/dashboard).
   - Select your project or create a new one.
   - Click "+ ENABLE APIS AND SERVICES" and search for "text-to-speech".
   - Enable the "Cloud Text-to-Speech API".

2. Add the Cloud Text-to-Speech API permission to your API key:
   - Go to [Google Cloud Credentials](https://console.cloud.google.com/apis/credentials).
   - Select your API key and add the Cloud Text-to-Speech API under API Restrictions.

## Testing

### Running Tests with Poetry

To run tests, use Poetry to execute the pytest command. This ensures that the tests are run within the virtual environment managed by Poetry.

```bash
poetry run pytest
```

This command will run all tests located in the `test` directory, including both end-to-end and unit tests, using the configuration specified in `pyproject.toml`.

Ensure that the server is running locally on `http://127.0.0.1:4000` before executing the end-to-end tests.
