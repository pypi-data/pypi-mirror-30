__version__ = "0.0.1"


import yaml
import click
import psycopg2
from statsd import StatsClient


@click.command(context_settings={
    "auto_envvar_prefix": "SQL2STATSD",
    "help_option_names": ["-h", "--help"]
})
@click.option(
    "--config-file",
    type=click.File(),
    default="config.yaml",
    show_default=True
)
@click.argument("job-name")
def main(config_file, job_name):
    """
    `sql2statsd` is a CLI utility that queries SQL database and posts results
    to StatsD based on provided YAML config file and job name.
    """
    config = yaml.load(config_file)

    job = config["jobs"][job_name]

    db_server = config["db_servers"][job["db_server"]]
    conn = psycopg2.connect(
        host=db_server["host"],
        port=db_server["port"],
        user=db_server["user"],
        password=db_server["password"],
        dbname=job["db_name"]
    )

    stats_server = config["stats_servers"][job["stats_server"]]
    stats = StatsClient(
        host=stats_server["host"],
        port=stats_server["port"]
    )

    with conn, conn.cursor() as cur:
        cur.execute(job["query"])
        assert cur.rowcount == 1, "Query must return exactly one row."

        row = cur.fetchone()
        assert len(row) == 1, "Query must return exactly one column."

    stats.gauge(job["stat"], row[0])

    conn.close()
