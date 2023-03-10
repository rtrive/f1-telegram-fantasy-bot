FROM ultrafunk/undetected-chromedriver:3.20-chrome-lateinstall

WORKDIR /app

ADD pyproject.toml poetry.lock /app/

RUN pip install --upgrade pip
RUN pip install poetry
RUN poetry config virtualenvs.in-project true
RUN poetry install --no-ansi

ADD . /app
CMD ["poetry run python src/main.py"]

