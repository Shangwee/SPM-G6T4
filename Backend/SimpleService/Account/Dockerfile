FROM python:3-slim
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt
EXPOSE 5001
COPY ./account_test.py .
COPY ./account.py .
CMD [ "python", "./account.py" ]