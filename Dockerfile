FROM alpine:latest
WORKDIR /opt/app

RUN apk --no-cache add python3 py3-pip py3-requests py3-prometheus-client \
 && pip3 install --no-cache-dir --disable-pip-version-check metar \
 && apk del py3-pip

COPY main.py ./

EXPOSE 3000
ENTRYPOINT ["python", "main.py"]

ARG BUILD_DATE="Unknown"
ARG SOURCE_COMMIT="Unknown"
LABEL \
    maintainer="" \
    org.opencontainers.image.title="ghcr.io/sgsunder/prometheus-metar" \
    org.opencontainers.image.url="https://github.com/sgsunder/prometheus-metar" \
    org.opencontainers.image.created="${BUILD_DATE}" \
    org.opencontainers.image.source="https://github.com/sgsunder/prometheus-metar" \
    org.opencontainers.image.revision="${SOURCE_COMMIT}" \
    org.opencontainers.image.licenses="GPL-3.0"