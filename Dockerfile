FROM python:3.11-rc-bullseye
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt # Write Flask in this file
EXPOSE 5001 
ENTRYPOINT [ "python" ] 
CMD [ "app.py" ]