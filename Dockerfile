FROM python:3.12-slim
WORKDIR /app
COPY server.py index.html ./
ENV PYTHONDONTWRITEBYTECODE=1 PORT=10000
EXPOSE 10000
CMD ["python","-u","server.py"]
