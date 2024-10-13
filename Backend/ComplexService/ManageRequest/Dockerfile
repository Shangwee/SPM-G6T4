FROM python:3-slim
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY ./manage_request.py .
COPY ./manage_request_test.py .
CMD [ "python", "./manage_request.py" ]