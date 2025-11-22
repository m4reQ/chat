# Chat app
This is a fully fledged chat web application, using websockets for efficient message exchange. It contains its frontend written in Typescript, using React, as well as Python API and MySQL database.

## Installation
Getting up the application is simple and requires only few steps.

### Environment files
First thing you should do after cloning the repository is to find all `.env-template` files and fill in their contents as appropriate.
All values inside are documented. Next change all of these files names' to `.env` for docker-compose to be able to find them.

### Email server certificates
If you plan to use TLS you need to include SSL certificates in the "chat-email/certificates" directory. You might need to also adjust "maddy.conf" in the same directory (see: [TLS configuration](https://maddy.email/reference/tls/)).

### Building image and running container
> **_NOTE:_** This application uses docker for runtime and docker compose for orchestrating build.

To build and start the container use `docker-compose up --build`. Ensure that Docker Desktop or any
other docker provider is running on the target machine. This will build the image and start all services.
# Chat app
This is a fully fledged chat web application, using websockets for efficient message exchange. It contains its frontend written in Typescript, using React, as well as Python API and MySQL database.

## Installation
Getting up the application is simple and requires only few steps.

### Environment files
First thing you should do after cloning the repository is to find all `.env-template` files and fill in their contents as appropriate.
All values inside are documented. Next change all of these files names' to `.env` for docker-compose to be able to find them.

### Email server certificates
If you plan to use TLS you need to include SSL certificates in the "chat-email/certificates" directory. You might need to also adjust "maddy.conf" in the same directory (see: [TLS configuration](https://maddy.email/reference/tls/)).

### Building image and running container
> **_NOTE:_**  
> This application uses docker for runtime and docker compose for orchestrating build.

To build and start the container use `docker-compose up --build`. Ensure that Docker Desktop or any
other docker provider is running on the target machine. This will build the image and start all services.

## Documentation
API docs are available out-of-the-box when using development mode. After starting the application simply go to `http://localhost:8000/docs` or `http://localhost:8000/redoc`.
> **_NOTE:_**  
> You might need to change address and base port to match ones defined for the API service, when building docker image.

## Known issues
- Currently built frontend container doesn't work correctly and fails to load CSS stylesheets. This is probably due to invalid nginx configuration and should be fixed soon. For now we recommend running frontend app locally using `npm start`.
> **_NOTE:_**  
> When running application locally, environment variables must be provided manually. To correctly run the app set them before like so:  
>  
> **Bash**  `set API_KEY=<your api key> && set API_BASE_URL=<docker API container url> && npm start`  
> **Powershell** `$env:API_KEY=<your api key>; $env:API_BASE_URL=<docker API container url>; npm start`  
## Documentation
API docs are available out-of-the-box when using development mode. After starting the application simply go to `http://localhost:8000/docs` or `http://localhost:8000/redoc`.
> **_NOTE:_** You might need to change address and base port to match ones defined for the API service, when building docker image.

## Known issues
- Currently built frontend container doesn't work correctly and fails to load CSS stylesheets. This is probably due to invalid nginx configuration and should be fixed soon. For now we recommend running frontend app locally using `npm start`.
>>> **_NOTE:_** When running application locally, environment variables must be provided manually.
>>> To correctly run the app set them before like so:  
- bash: `set API_KEY=<your api key> && set API_BASE_URL=<docker API container url> && npm start`  
- ps: `$env:API_KEY=<your api key>; $env:API_BASE_URL=<docker API container url>; npm start`  