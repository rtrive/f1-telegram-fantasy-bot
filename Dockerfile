FROM selenium/standalone-chrome

USER root
RUN apt-get update && apt-get install software-properties-common python3-distutils xvfb  -y && apt update
RUN add-apt-repository ppa:deadsnakes/ppa && apt update
RUN apt-get install python3.11 -y
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3 get-pip.py

ENV DISPLAY=:1

WORKDIR /app

ADD pyproject.toml poetry.lock /app/

RUN pip install --upgrade pip
RUN pip install poetry
RUN poetry config virtualenvs.in-project true
RUN poetry install --no-ansi

ADD . /app
RUN Xvfb $DISPLAY -screen $DISPLAY 1280x1024x16 &
CMD /app/.venv/bin/python src/main.py

