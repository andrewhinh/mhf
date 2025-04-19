import os
from datetime import datetime
from pathlib import Path

import modal
from utils import (
    APP_NAME,
    ARTIFACTS_PATH,
    CPU,
    MEM,
    MINUTES,
    PYTHON_VERSION,
    RUNS_VOLUME,
    SECRETS,
    SRC_PATH,
    VOLUME_CONFIG,
)

# Modal

image = (
    modal.Image.debian_slim(python_version=PYTHON_VERSION)
    .pip_install(
        "fastapi>=0.115.8",
        "locust>=2.33.0",
        "requests>=2.32.3",
        "pillow>=10.4.0",
        "pydantic>=2.10.6",
        "python-dotenv>=1.0.1",
    )
    .add_local_file(
        SRC_PATH / "locustfile.py",
        remote_path="/root/locustfile.py",
        copy=True,
    )
    .add_local_dir(ARTIFACTS_PATH, "/artifacts")
)

app = modal.App(
    name=f"{APP_NAME}-load-test", image=image, volumes=VOLUME_CONFIG, secrets=SECRETS
)

TIMEOUT = 60 * MINUTES
ALLOW_CONCURRENT_INPUTS = 1000

# locust

OUT_DIRECTORY = (
    Path(f"/{RUNS_VOLUME}") / datetime.utcnow().replace(microsecond=0).isoformat()
)
PORT = 8089
RATE = 1
USERS = 36
TIME = "5m"  # < TIMEOUT

default_args = [
    "-H",
    os.getenv("API_URL"),
    "--processes",
    str(CPU),
    "--csv",
    OUT_DIRECTORY / "stats.csv",
]


@app.function(cpu=CPU, memory=MEM, timeout=TIMEOUT)
def run_locust(args: list, wait=False):
    import subprocess

    process = subprocess.Popen(["locust"] + args)
    if wait:
        process.wait()
        return process.returncode


@app.function(cpu=CPU, memory=MEM)
@modal.concurrent(max_inputs=ALLOW_CONCURRENT_INPUTS)
@modal.web_server(port=PORT)
def serve_locust():
    run_locust.local(default_args)


def main(r: float = RATE, u: int = USERS, t: str = TIME):
    args = default_args + [
        "--spawn-rate",
        str(r),
        "--users",
        str(u),
        "--run-time",
        t,
    ]

    html_report_file = OUT_DIRECTORY / "report.html"
    args += [
        "--headless",  # run without browser UI
        "--autostart",  # start test immediately
        "--autoquit",  # stop once finished...
        "10",  # ...but wait ten seconds
        "--html",  # output an HTML-formatted report
        html_report_file,  # to this location
    ]

    if exit_code := run_locust.remote(args, wait=True):
        SystemExit(exit_code)
    else:
        print("finished successfully")


@app.local_entrypoint()
def test(
    r: float = RATE,
    u: int = USERS,
    t: str = TIME,
):
    main(r, u, t)
