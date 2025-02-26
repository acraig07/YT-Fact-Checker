FROM python:3.12
WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 5000

ENTRYPOINT ["python"]
CMD ["app.py"]