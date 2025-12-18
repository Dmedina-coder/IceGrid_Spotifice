FROM zeroc/icegridnode:3.7.10

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3-zeroc-ice \
        zeroc-ice-all-dev \
        python3-gi \
        gir1.2-gstreamer-1.0 \
        gir1.2-gst-plugins-base-1.0 \
        iproute2 \
        gstreamer1.0-plugins-base \
        gstreamer1.0-plugins-good \
        gstreamer1.0-tools \
        net-tools && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
