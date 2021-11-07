FROM python:3.9-bullseye
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt # Write Flask in this file
EXPOSE 5000
ENTRYPOINT [ "python" ]
CMD [ "app.py" ]