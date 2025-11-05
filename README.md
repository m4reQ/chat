# Chat app
This is a fully fledged chat web application, using websockets for efficient message exchange. It contains its frontend written in Typescript, using React, as well as Python API and MySQL database.
## Installation
> **_NOTE:_** This application uses docker for runtime and docker compose for orchestrating build.

Getting up the application is simple and requires only few commands. After cloning this repository, navigate to the root directory and invoke

`docker-compose up --build`

This will build the image and start all services. Application requires some previous setup which will be documented later.
## Documentation
API docs are available out-of-the-box when using development mode. After starting the application simply go to `http://localhost:8000/docs` or `http://localhost:8000/redoc`.
> **_NOTE:_** You might need to change address and base port to match ones defined for the API service, when building docker image.