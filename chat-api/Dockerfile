FROM python:3.14

WORKDIR /api

COPY ./requirements.txt /api/requirements.txt

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --no-cache-dir --upgrade -r /api/requirements.txt

COPY ./app /api/app

CMD ["fastapi", "run", "app/main.py", "--port", "8000"]