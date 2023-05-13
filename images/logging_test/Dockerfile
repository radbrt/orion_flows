FROM prefecthq/prefect:2.10.9-python3.9


RUN apt update && \
    apt upgrade -y && \
    apt install -y libpq-dev

COPY requirements.txt requirements.txt
COPY logging_script.py logging_script.py

RUN pip install -r requirements.txt
