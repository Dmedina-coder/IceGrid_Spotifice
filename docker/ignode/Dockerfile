FROM zeroc/icegridnode:3.7

# Install Python Ice from PyPI (includes Ice.Py3) and keep minimal tools for debugging
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3-pip \
        python3-dev \
        build-essential \
        libssl-dev \
        libbz2-dev \
        iproute2 \
        net-tools && \
    pip3 install --no-cache-dir "zeroc-ice==3.7.10.1" && \
    apt-get purge -y python3-dev build-essential libssl-dev libbz2-dev && \
    apt-get autoremove -y && \
    apt-get clean && rm -rf /var/lib/apt/lists/*