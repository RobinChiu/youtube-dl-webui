FROM python:3.7
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl git unzip wget \
        ffmpeg \
        tzdata pkg-config && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* && \
    apt-get autoclean && \
    apt-get clean

# install gradio
RUN python3 -m pip install --upgrade pip
RUN pip install --no-cache-dir gradio

# install the youtube-dl
ADD youtube-dl /youtube-dl
WORKDIR /youtube-dl
RUN pip install -e .

ARG APP_ROOT=/usr/src/app
RUN mkdir -p $APP_ROOT
RUN mkdir -p $APP_ROOT/downloads
WORKDIR $APP_ROOT
COPY app .

WORKDIR $APP_ROOT
EXPOSE 7860
CMD ["python", "web-ui.py"]


