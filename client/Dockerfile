FROM python:3.10
WORKDIR /src/app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN mkdir -p received

ENV FLASK_RUN_PORT 8001
EXPOSE 8001
CMD ["flask", "run", "--debug", "--host=0.0.0.0"]
