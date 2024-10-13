FROM python:3-slim
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
COPY ./request_test.py .
COPY ./request.py .
CMD [ "python", "./request.py" ]