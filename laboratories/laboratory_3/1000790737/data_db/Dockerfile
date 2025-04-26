FROM python:3.12.6

RUN python -m pip install --upgrade pip
RUN mkdir -p /home/backend/app
WORKDIR /home/backend/app

COPY . .

RUN pip install flask

CMD ["python", "money_database.py"]