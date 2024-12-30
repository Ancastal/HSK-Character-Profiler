import collections
from jieba import cut
import json
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import track
from rich.panel import Panel
from rich.text import Text

console = Console()
level_sets = [set() for _ in range(7)]

# Add HSK level colors
HSK_COLORS = {
    1: "bright_green",
    2: "green",
    3: "blue",
    4: "yellow",
    5: "red",
    6: "magenta",
    7: "bright_magenta"
}

def show_welcome_banner():
    welcome_text = """
    [bold cyan]HSK Text Profiler[/]
    Analyze the complexity of Chinese texts based on HSK levels
    
    [bold yellow]Usage:[/]
    1. Place your Chinese text in 'characters.txt'
    2. Run the program to see detailed HSK analysis
    3. Results will be saved automatically
    
    [bold green]Loading HSK data...[/]
    """
    console.print(Panel(welcome_text, border_style="cyan"))

def load_hsk_files():
    try:
        for hsk_levels in track(range(1, 8), description="Loading HSK levels..."):
            with open(f'hsk{hsk_levels}.txt', 'r', encoding='utf-8') as file:
                hsk_set = set()
                for line in file:
                    character = line.strip()
                    hsk_set.add(character)
                    found = False
                    for i in range(1, hsk_levels):
                        if character in level_sets[i-1]:
                            found = True
                            break
                    if not found:
                        level_sets[hsk_levels-1].add(character)
        console.print("[bold green]✓[/] HSK files loaded successfully!")
    except FileNotFoundError as e:
        console.print(f"[bold red]Error:[/] HSK file not found - {e}")
        raise
    except Exception as e:
        console.print(f"[bold red]Error loading HSK files:[/] {e}")
        raise

def find_hsk_level(character):
    for level, level_set in enumerate(level_sets):
        if character in level_set:
            return level+1
    return None

def analyze_frequent_chars(text, top_n=10):
    """Analyze most frequent characters in the text."""
    char_freq = collections.Counter(text)
    return char_freq.most_common(top_n)

def save_results(stats, filepath='hsk_analysis_results.json'):
    """Save analysis results to a JSON file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    console.print(f"[bold green]✓[/] Results saved to [cyan]{filepath}[/]")

def profiler(path='characters.txt', save_output=False):
    try:
        show_welcome_banner()

        n_characters = 0
        counter = [0 for i in range(7)]
        not_found_characters = []
        not_found_number = 0
        
        with open(path, 'r', encoding='utf-8') as file:
            text = file.read()
            words = list(cut(text))
            
            with console.status("[bold green]Analyzing text complexity...") as status:
                for i, word in enumerate(words):
                    if i % 100 == 0:  # Update status periodically
                        status.update(f"Analyzed {i}/{len(words)} words...")
                    for character in word:
                        n_characters += 1
                        level = find_hsk_level(character)
                        if level is not None:
                            counter[level-1] += 1
                        else:
                            not_found_characters.append(character)
                            not_found_number += 1

        # Calculate statistics
        total_characters = sum(counter)
        stats = {
            "timestamp": datetime.now().isoformat(),
            "file_analyzed": path,
            "total_characters": n_characters,
            "hsk_statistics": {},
            "unknown_characters": {
                "count": not_found_number,
                "percentage": (not_found_number / n_characters * 100) if n_characters > 0 else 0,
                "examples": list(set(not_found_characters))[:10]
            }
        }

        # Create and display HSK level statistics table
        table = Table(title="[bold]HSK Level Distribution[/]", show_header=True, header_style="bold magenta")
        table.add_column("HSK Level", style="cyan", justify="center")
        table.add_column("Characters", style="green", justify="right")
        table.add_column("Count", style="yellow", justify="right")
        table.add_column("Percentage", style="yellow", justify="right")

        for level, count in enumerate(counter):
            percentage = (count / n_characters * 100) if n_characters > 0 else 0
            level_color = HSK_COLORS[level + 1]
            sample_chars = [char for char in text if find_hsk_level(char) == level + 1][:5]
            table.add_row(
                f"[{level_color}]Level {level+1}[/]",
                f"[{level_color}]{' '.join(sample_chars)}[/]" if sample_chars else "-",
                str(count),
                f"[{level_color}]{percentage:.1f}%[/]"
            )

        console.print("\n")
        console.print(table)

        # Calculate and display summary
        if total_characters > 0:
            average_hsk_level = sum((level+1) * count for level, count in enumerate(counter)) / total_characters
            summary = Table.grid()
            summary.add_column(style="bold cyan", justify="right")
            summary.add_column(style="yellow")
            summary.add_row("Total Characters:", str(n_characters))
            summary.add_row("Average HSK Level:", f"{average_hsk_level:.2f}")
            summary.add_row("Known Characters:", f"{(n_characters - not_found_number) / n_characters * 100:.1f}%")
            
            console.print("\n[bold]Summary:[/]")
            console.print(Panel(summary, border_style="cyan"))

        # Create and display frequent characters table
        freq_table = Table(title="Most Frequent Characters", show_header=True, header_style="bold magenta")
        freq_table.add_column("Character", style="cyan", justify="center")
        freq_table.add_column("Frequency", style="green", justify="right")
        freq_table.add_column("HSK Level", style="yellow", justify="center")

        frequent_chars = analyze_frequent_chars(text)
        stats["frequent_characters"] = []
        for char, freq in frequent_chars:
            level = find_hsk_level(char)
            stats["frequent_characters"].append({
                "character": char,
                "frequency": freq,
                "hsk_level": level
            })
            freq_table.add_row(
                char,
                str(freq),
                str(level) if level else "Unknown"
            )

        console.print(freq_table)

        # Display unknown characters analysis
        if not_found_characters:
            unknown_panel = Panel(
                f"Total unknown characters: [bold red]{not_found_number}[/] ([yellow]{(not_found_number/n_characters*100):.1f}%[/])\n"
                f"Sample: [cyan]{' '.join(list(set(not_found_characters))[:10])}[/]",
                title="Unknown Characters",
                border_style="red"
            )
            console.print(unknown_panel)

        if save_output:
            output_file = f"hsk_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            save_results(stats, output_file)

        return stats

    except FileNotFoundError:
        console.print(f"[bold red]Error:[/] Input file '{path}' not found")
        return None
    except Exception as e:
        console.print(f"[bold red]Error during analysis:[/] {e}")
        return None

if __name__ == "__main__":
    # Initialize HSK data
    try:
        load_hsk_files()
        # Example usage
        results = profiler("characters.txt", save_output=True)
    except Exception as e:
        console.print(f"[bold red]Failed to initialize HSK Profiler:[/] {e}")
