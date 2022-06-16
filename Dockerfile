FROM ultrafunk/undetected-chromedriver:latest

WORKDIR /app

ADD pyproject.toml poetry.lock /app/

RUN pip install --upgrade pip
RUN pip install poetry
RUN poetry config virtualenvs.in-project true
RUN poetry install --no-ansi

ADD . /app
CMD /app/.venv/bin/python src/main.py

