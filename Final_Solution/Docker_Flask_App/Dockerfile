# use an image (built earlier from Dockerfile.base) with pip dependencies installed
FROM chatmaja_base:v1

# arbitrary directory name, inside the container
WORKDIR /app

# copy from this directory to /app in the container all files according to .dockerignore
COPY ./app/ /app

EXPOSE 5000

# for saving models downloaded from huggingface
ENV HF_HOME=/app/models
# LanceDB was showing errors when trying to save to /root/ folder
ENV LANCEDB_CONFIG_DIR=/app/db_config

# for Flask to know which file to run (default is app.py)
ENV FLASK_APP=app.py

# --host allows acessing Flask in Docker container from any address, including localhost
CMD ["python3", "-m" , "flask", "run", "--host=0.0.0.0"]
