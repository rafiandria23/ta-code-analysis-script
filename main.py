import typer
import os
from rich.console import Console
from rich.panel import Panel
from services.github_service import GitHubService
from services.gemini_service import GeminiService
import config

app = typer.Typer(help="CLI tool to analyze GitHub repositories using Gemini AI.")
console = Console()

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """
    Default entry point. If no command is provided, it runs the 'report' command.
    """
    if ctx.invoked_subcommand is None:
        run_report_logic()

def get_credentials():
    """Get GitHub credentials by prompting the user."""
    # Always ask for username
    username = typer.prompt("What's your GitHub username?")
    
    # Always ask for PAT, required for GraphQL API
    token = typer.prompt("What's your GitHub PAT?", hide_input=True)
    
    return username, token

def run_report_logic(username: str = None, days: int = 7):
    """Internal logic for generating the report."""
    try:
        # Get credentials
        user_name, token = get_credentials()
        target_username = username or user_name
        
        if not target_username:
            console.print("[bold red]Error:[/] Username is required.")
            return

        github = GitHubService(token=token)
        gemini = GeminiService()

        with console.status(f"[bold green]Fetching activity for {target_username}..."):
            commits = github.get_user_activity(target_username, days=days)
            stats = github.calculate_stats(commits)
        
        if not commits:
            console.print(f"[yellow]No commits found for {target_username} in the last {days} days.[/]")
            return

        with console.status("[bold blue]Analyzing code quality with Gemini..."):
            analysis = gemini.analyze_quality(commits)
        
        # Display Stats
        console.print(Panel(
            f"[bold]Total Commits:[/] {stats['total_commits']}\n"
            f"[bold]Avg Time Between Pushes:[/] {stats['avg_time_between_pushes']}",
            title="Activity Stats", border_style="cyan"
        ))

        # Display AI Analysis
        console.print(Panel(analysis, title=f"AI Quality Report for {target_username}", border_style="magenta"))
    
    except Exception as e:
        console.print(f"[bold red]Error:[/] {str(e)}")

@app.command()
def report(username: str = typer.Option(None, help="GitHub username"), 
           days: int = typer.Option(7, help="Number of days to look back")):
    """Generate a 7-day activity and quality report."""
    run_report_logic(username=username, days=days)

@app.command()
def summarize(repo_name: str = typer.Argument(..., help="GitHub repository name (e.g., 'owner/repo')")):
    """Summarize a GitHub repository's purpose and README."""
    try:
        github = GitHubService()
        gemini = GeminiService()

        with console.status(f"[bold green]Fetching details for {repo_name}..."):
            details = github.get_repo_details(repo_name)
        
        with console.status("[bold blue]Generating summary with Gemini..."):
            summary = gemini.summarize_repo(details)
        
        console.print(Panel(summary, title=f"Summary of {repo_name}", border_style="blue"))
    
    except Exception as e:
        console.print(f"[bold red]Error:[/] {str(e)}")

@app.command()
def analyze_activity(repo_name: str = typer.Argument(..., help="GitHub repository name (e.g., 'owner/repo')"), 
                    count: int = typer.Option(5, help="Number of recent commits to analyze")):
    """Analyze recent development activity based on commits."""
    try:
        github = GitHubService()
        gemini = GeminiService()

        with console.status(f"[bold green]Fetching recent commits for {repo_name}..."):
            commits = github.get_recent_commits(repo_name, count=count)
        
        with console.status("[bold blue]Analyzing activity with Gemini..."):
            analysis = gemini.analyze_commits(repo_name, commits)
        
        console.print(Panel(analysis, title=f"Activity Analysis for {repo_name}", border_style="green"))
    
    except Exception as e:
        console.print(f"[bold red]Error:[/] {str(e)}")

if __name__ == "__main__":
    app()
