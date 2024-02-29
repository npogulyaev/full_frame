FROM python:3.8-bookworm

#ENV DEBIAN_FRONTEND noninteractive
#RUN apt-get update -y
#RUN apt-get install python3-pip python3.8-dev gcc ffmpeg tesseract-ocr libx264-dev -y
#ARG DEBIAN_FRONTEND=noninteractive

COPY requirements.txt .
#RUN apt-get install python3-pip -y
RUN python3 -m pip install --upgrade pip
# RUN python3 -m pip uninstall -y nvidia-tensorboard nvidia-tensorboard-plugin-dlprof
RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY logger.py main.py ./

CMD python3 -u main.py