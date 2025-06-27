FROM python:3.12.4

WORKDIR /Academhub

COPY Academhub .

RUN pip install -r requirements.txt

COPY start.sh .

RUN chmod 777 start.sh

ENTRYPOINT ["sh", "./start.sh"]