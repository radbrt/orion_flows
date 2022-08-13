FROM prefecthq/prefect:2.0.4-python3.10


RUN apt update && \
    apt upgrade -y && \
    apt install -y libpq-dev
ADD requirements.txt requirements.txt

RUN pip install -r requirements.txt
