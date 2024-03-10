FROM prefecthq/prefect:2.14.17-python3.11


RUN apt update && \
    apt upgrade -y && \
    apt install -y libpq-dev
ADD requirements.txt requirements.txt

RUN pip install -r requirements.txt
