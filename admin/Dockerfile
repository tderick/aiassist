# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.11-bullseye

EXPOSE 5000
# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1
WORKDIR /app



# Install pip requirements
COPY ./requirements.txt /app
RUN pip install --upgrade pip
RUN  pip install --no-cache-dir --upgrade -r requirements.txt

COPY . /app

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser
# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
# CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"] # run this when uwgi is not considered
# start uWSGI using config file
CMD ["uwsgi","app.ini"]
