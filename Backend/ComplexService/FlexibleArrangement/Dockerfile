FROM python:3-slim
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY ./flexible_arrangement.py .
COPY ./flexible_arrangement_test.py .
CMD [ "python", "./flexible_arrangement.py" ]