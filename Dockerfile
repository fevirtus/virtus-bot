FROM python:3.9

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen

COPY . .

RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uv", "run", "python", "main.py"] 