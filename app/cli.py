import typer, json
from app.rules.engine import run_engine
from app.collectors.aws_collector import AWSCollector

app = typer.Typer(help="Mini Greenlight Engine — ADA Cloud Config audit CLI")

@app.command()
def scan(input_file: str = "app/rules/schema_example.json", output_dir: str = "results"):
    """Run the rule engine against a cloud state file."""
    with open(input_file) as f:
        state = json.load(f)
    report = run_engine(state)
    typer.echo(f"Risk score: {report['risk_score']}/100")
    typer.echo(f"Passed: {report['summary']['passed']} | Failed: {report['summary']['failed']}")
    with open(f"{output_dir}/report.json", "w") as f:
        json.dump(report, f, indent=2)

@app.command()
def version():
    """Show the engine version."""
    typer.echo("Mini Greenlight Engine v0.1.0")

@app.command()
def scan_live(endpoint_url: str = "http://localhost:4566", output_dir: str = "results"):
    """Collect live state from LocalStack and run the engine against it."""
    collector = AWSCollector(endpoint_url=endpoint_url)
    state = collector.collect_all()
    report = run_engine(state)
    typer.echo(f"Risk score: {report['risk_score']}/100")
    with open(f"{output_dir}/live_report.json", "w") as f:
        json.dump(report, f, indent=2)
        
if __name__ == "__main__":
    app()