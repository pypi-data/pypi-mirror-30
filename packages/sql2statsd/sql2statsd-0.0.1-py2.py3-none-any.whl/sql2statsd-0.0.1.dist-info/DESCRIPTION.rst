# sql2statsd

`sql2statsd` is a CLI utility that queries SQL database and posts results to
[StatsD](https://github.com/etsy/statsd)
based on a provided YAML config file and a job name.


## Installation

`virtualenv` recommended.

- From Github:
    ```
    pip install -e git+https://github.com/Suenweek/sql2statsd#egg=sql2statsd
    ```


## Usage
`sql2statsd` is intended to be run as a scheduled task (e.g. a `cron` job).

1. Create a YAML config file based on a config schema provided below.
2. Run `sql2statsd --config-file <CONFIG_FILE> <JOB_NAME>` where:
    - `<CONFIG_FILE>` is a path to your config.
    - `<JOB_NAME>` is a key in a `config["jobs"]` section.

Passing config file path as a parameter each time is tedious, so you may want
to specify `SQL2STATSD_CONFIG_FILE` env var instead.


## Config schema

```yaml
db_servers:
    <str>:  # Database server name
        host: <str>
        port: <int>
        user: <str>
        password: <str>

stats_servers:
    <str>:  # Stats server name
        host: <str>
        port: <int>

jobs:
    <str>:  # Job name
        db_server: <str>  # Database server name
        db_name: <str>
        stats_server: <str>  # Stats server name
        stat: <str>
        query: <str>
```


