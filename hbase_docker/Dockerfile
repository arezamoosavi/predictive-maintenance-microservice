FROM ubuntu:bionic

COPY ./hbase_docker/*.sh /build/

ENV HBASE_VERSION 2.1.2

RUN /build/prepare-hbase.sh && \
    cd /opt/hbase && /build/build-hbase.sh \
    cd / && /build/cleanup-hbase.sh && rm -rf /build

VOLUME /data

ADD ./hbase_docker/hbase-site.xml /opt/hbase/conf/hbase-site.xml

ADD ./hbase_docker/zoo.cfg /opt/hbase/conf/zoo.cfg

ADD ./hbase_docker/replace-hostname /opt/replace-hostname

ADD ./hbase_docker/hbase-server /opt/hbase-server

# REST API
EXPOSE 8080
# REST Web UI at :8085/rest.jsp
EXPOSE 8085
# Thrift API
EXPOSE 9090
# Thrift Web UI at :9095/thrift.jsp
EXPOSE 9095
# HBase Master web UI at :16010/master-status;  ZK at :16010/zk.jsp
EXPOSE 16010

CMD ["/opt/hbase-server"]
