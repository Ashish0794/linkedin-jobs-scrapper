FROM python:3.9-slim

USER root

WORKDIR /opt/linkedin-jobs-scrapper

#RUN apt-get update && apt-get install -y build-essential curl unzip wget gnupg

RUN apt-get update && apt-get install -yqq build-essential curl unzip wget gnupg unzip

# Adding trusting keys to apt for repositories
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -

# Adding Google Chrome to the repositories
RUN echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list

# Magic happens
RUN apt-get update && apt-get install -y google-chrome-stable

# Installing Unzip
#RUN apt-get install -yqq unzip

# Download the Chrome Driver
RUN wget -O /tmp/chromedriver.zip chromedriver.storage.googleapis.com/102.0.5005.61/chromedriver_linux64.zip

# Unzip the Chrome Driver into /usr/local/bin directory
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./linkedin-jobs-scrapper ./codes
WORKDIR /opt/linkedin-jobs-scrapper/codes

CMD tail -f /dev/null

#CMD ["python", "main.py"]

