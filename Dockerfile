# app/Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install -y 

RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app_V3.py", "--server.port=8501", "--server.address=0.0.0.0"]