FROM prefecthq/prefect:2.0b5-python3.9

RUN apt update
RUN apt upgrade -y

WORKDIR /
ADD requirements.txt /requirements.txt

RUN pip install -r /requirements.txt