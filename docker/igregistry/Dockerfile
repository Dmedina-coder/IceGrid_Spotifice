FROM ubuntu:22.04

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    zeroc-icegrid iproute2 net-tools && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

CMD ["/usr/bin/icegridregistry", "--Ice.Config=/etc/icegridregistry.conf"]
