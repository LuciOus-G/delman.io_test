FROM python:3.7

# copy the requirements file into the image
COPY ./requirements.txt /app/requirements.txt

# switch working directory
WORKDIR /app

# set environment variable
ENV DB_HOST 'db'
ENV DB_PORT '5432'

# insalling psycopg
RUN apt-get update && \
    apt-get -y install gcc musl-dev && \
    apt-get -y install netcat-openbsd

RUN apt-get update && apt-get -y install libpq-dev gcc python3-dev musl-dev && \
    pip install psycopg2-binary

# install the dependencies and packages in the requirements file
RUN pip install -r requirements.txt


# copy every content from the local file to the image
COPY . /app

RUN chmod u+x ./start.sh

# configure the container to run in an executed manner
CMD ["./start.sh"]