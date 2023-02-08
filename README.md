Prometheus exporter used to scrape weather information from METAR stations:

### Usage

Use the following docker-compose snippet to run the scraper alongside your prometheus container
```yaml
metric-metar:
  image: ghcr.io/sgsunder/prometheus-metar:latest
  networks:
    - metrics  # ensure that your prometheus container has access to the same docker network
  command: ["KJFK", "EGLL", "RJTT"]  # enter one or more ICAO airport codes for which to scrape
```

Then in your `prometheus.yml` file, include something like this under `scrape_configs`:
```yaml
- job_name: 'metar'
  scrape_interval: 30m
  static_configs:
  - targets: ['metric-metar:3000']
```
