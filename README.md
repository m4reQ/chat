# Chat app
This is a fully fledged chat web application, using websockets for efficient message exchange. It contains its frontend written in Typescript, using React, as well as Python API and MySQL database.

## Installation
Getting up the application is simple and requires only few steps.

### Environment files
First thing you should do after cloning the repository is to find all `.env-template` files and fill in their contents as appropriate.
All values inside are documented. Next change all of these files names' to `.env` for docker-compose to be able to find them.

### Building image and running container
> **_NOTE:_** This application uses docker for runtime and docker compose for orchestrating build.
To build and start the container use `docker-compose up --build`. Ensure that Docker Desktop or any
other docker provider is running on the target machine. This will build the image and start all services.


## Documentation
API docs are available out-of-the-box when using development mode. After starting the application simply go to `http://localhost:8000/docs` or `http://localhost:8000/redoc`.
> **_NOTE:_** You might need to change address and base port to match ones defined for the API service, when building docker image.