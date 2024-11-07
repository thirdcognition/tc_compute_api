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

## Testing

### Running Tests with Poetry

To run tests, use Poetry to execute the pytest command. This ensures that the tests are run within the virtual environment managed by Poetry.

```bash
poetry run pytest
```

This command will run all tests located in the `test` directory, including both end-to-end and unit tests, using the configuration specified in `pyproject.toml`.

Ensure that the server is running locally on `http://127.0.0.1:4000` before executing the end-to-end tests.
