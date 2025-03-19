FROM python

WORKDIR /Academhub

COPY Academhub /Academhub

RUN pip install -r requirements.txt

COPY start.sh .

CMD ["./start.sh"]