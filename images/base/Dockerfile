FROM prefecthq/prefect:2.6.1-python3.9


RUN apt update && \
    apt upgrade -y && \
    apt install -y libpq-dev
ADD requirements.txt requirements.txt

RUN pip install -r requirements.txt
