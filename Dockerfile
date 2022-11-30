# Dockerfile should always start with FROM (base image/OS)
# inspect the Dokerfiles for these images but these already contains the OS!!!
FROM python:3.10-buster

# use an email address for the maintainer
LABEL maintainer="Nazarkoss"

WORKDIR /code

# Creates a new layer???
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

#COPY ./fastapi_exploration /code/fastapi_exploration
COPY ./ /code/

#WORKDIR /code/fastapi_exploration

# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
CMD ["uvicorn", "local_json_storage_api.carsharing_json:app", "--host", "0.0.0.0", "--port", "80"]
