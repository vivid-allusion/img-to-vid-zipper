#!/usr/bin/env python3
"""IMG-TO-VID Markdown Zipper - Pairs URLs with prompts to generate structured MD files."""

import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Dict, Optional
from urllib.parse import urlparse
import requests
from alive_progress import alive_bar
from loguru import logger
from natsort import natsorted
from rich.console import Console

console = Console()
BASE_DIR = Path(__file__).parent.parent
PROMPTS_DIR = BASE_DIR / "USER-FILES" / "04.INPUT" / "04.1_PROMPTS"
NUM_FRAMES_DIR = BASE_DIR / "USER-FILES" / "04.INPUT" / "04.2_NUM_FRAMES"
LINKS_DIR = BASE_DIR / "USER-FILES" / "04.INPUT" / "04.3_IMG_LINKS"
OUTPUT_BASE = BASE_DIR / "USER-FILES" / "05.OUTPUT"


def validate_folders_exist() -> None:
    """Validate that all three input folders exist, exit if missing."""
    if not PROMPTS_DIR.exists():
        console.print(f"[red]✗ Error: PROMPTS folder not found: {PROMPTS_DIR}[/red]")
        sys.exit(1)
    if not LINKS_DIR.exists():
        console.print(f"[red]✗ Error: LINKS folder not found: {LINKS_DIR}[/red]")
        sys.exit(1)
    if not NUM_FRAMES_DIR.exists():
        console.print(
            f"[red]✗ Error: NUM_FRAMES folder not found: {NUM_FRAMES_DIR}[/red]"
        )
        sys.exit(1)


def discover_txt_files(folder: Path) -> List[Path]:
    """Discover and sort .txt files using natural sort."""
    return natsorted(list(folder.glob("*.txt")))


def validate_file_counts(links_files: List[Path], prompts_files: List[Path]) -> None:
    """Verify equal count of .txt files, exit if mismatch."""
    if len(links_files) != len(prompts_files):
        console.print(f"[red]✗ Error: File count mismatch[/red]")
        console.print(f"  LINKS folder: {len(links_files)} .txt files")
        console.print(f"  PROMPTS folder: {len(prompts_files)} .txt files")
        console.print(f"\nBoth folders must have the same number of .txt files.")
        sys.exit(1)


def discover_subfolder_structure(base_dir: Path) -> Dict[str, List[Path]]:
    """Discover all subfolders and their .txt files with unlimited nesting depth.

    Returns dict mapping relative subfolder paths to sorted .txt file lists.
    Root-level files are stored under empty string key "".
    """
    structure: Dict[str, List[Path]] = {}

    # Get root-level .txt files
    root_files = natsorted(list(base_dir.glob("*.txt")))
    if root_files:
        structure[""] = root_files

    # Get all subdirectories recursively
    all_dirs = [d for d in base_dir.rglob("*") if d.is_dir()]

    # For each directory, get its .txt files
    for dir_path in all_dirs:
        relative_path = dir_path.relative_to(base_dir)
        txt_files = natsorted(list(dir_path.glob("*.txt")))
        if txt_files:
            structure[str(relative_path)] = txt_files

    return structure


def validate_subfolder_matching(
    prompts_structure: Dict[str, List[Path]],
    links_structure: Dict[str, List[Path]],
    num_frames_structure: Dict[str, List[Path]],
) -> None:
    """Validate that subfolders match between PROMPTS, LINKS, and NUM_FRAMES (case-insensitive).

    Fail fast if any subfolder exists in one directory but not the others.
    """
    # Normalize keys to lowercase for case-insensitive comparison
    prompts_keys_lower = {k.lower(): k for k in prompts_structure.keys()}
    links_keys_lower = {k.lower(): k for k in links_structure.keys()}
    num_frames_keys_lower = {k.lower(): k for k in num_frames_structure.keys()}

    prompts_only = (
        set(prompts_keys_lower.keys())
        - set(links_keys_lower.keys())
        - set(num_frames_keys_lower.keys())
    )
    links_only = (
        set(links_keys_lower.keys())
        - set(prompts_keys_lower.keys())
        - set(num_frames_keys_lower.keys())
    )
    num_frames_only = (
        set(num_frames_keys_lower.keys())
        - set(prompts_keys_lower.keys())
        - set(links_keys_lower.keys())
    )

    if prompts_only or links_only or num_frames_only:
        console.print(f"[red]✗ Error: Subfolder mismatch detected[/red]\n")

        if prompts_only:
            console.print(
                "[red]Subfolders in PROMPTS but not in LINKS/NUM_FRAMES:[/red]"
            )
            for key in sorted(prompts_only):
                original_key = prompts_keys_lower[key]
                display_name = "ROOT" if original_key == "" else original_key
                console.print(f"  - {display_name}")
            console.print()

        if links_only:
            console.print(
                "[red]Subfolders in LINKS but not in PROMPTS/NUM_FRAMES:[/red]"
            )
            for key in sorted(links_only):
                original_key = links_keys_lower[key]
                display_name = "ROOT" if original_key == "" else original_key
                console.print(f"  - {display_name}")
            console.print()

        if num_frames_only:
            console.print(
                "[red]Subfolders in NUM_FRAMES but not in PROMPTS/LINKS:[/red]"
            )
            for key in sorted(num_frames_only):
                original_key = num_frames_keys_lower[key]
                display_name = "ROOT" if original_key == "" else original_key
                console.print(f"  - {display_name}")
            console.print()

        console.print("All three directories must have matching subfolder structures.")
        sys.exit(1)


def validate_empty_subfolders(structure: Dict[str, List[Path]], dir_name: str) -> None:
    """Validate that no subfolders are empty.

    All discovered subfolders must contain at least one .txt file.
    """
    empty_subfolders = [path for path, files in structure.items() if not files]

    if empty_subfolders:
        console.print(f"[red]✗ Error: Empty subfolders detected in {dir_name}[/red]\n")
        for subfolder in sorted(empty_subfolders):
            display_name = "ROOT" if subfolder == "" else subfolder
            console.print(f"  - {display_name}")
        console.print(f"\nAll subfolders must contain at least one .txt file.")
        sys.exit(1)


def validate_per_subfolder_file_counts(
    prompts_structure: Dict[str, List[Path]],
    links_structure: Dict[str, List[Path]],
    num_frames_structure: Dict[str, List[Path]],
) -> None:
    """Validate that each matching subfolder has equal .txt file counts across all three folders."""
    # Use case-insensitive matching
    prompts_keys_lower = {k.lower(): k for k in prompts_structure.keys()}
    links_keys_lower = {k.lower(): k for k in links_structure.keys()}
    num_frames_keys_lower = {k.lower(): k for k in num_frames_structure.keys()}

    mismatches = []

    for key_lower in prompts_keys_lower.keys():
        prompts_key = prompts_keys_lower[key_lower]
        links_key = links_keys_lower[key_lower]
        num_frames_key = num_frames_keys_lower[key_lower]

        prompts_count = len(prompts_structure[prompts_key])
        links_count = len(links_structure[links_key])
        num_frames_count = len(num_frames_structure[num_frames_key])

        if prompts_count != links_count or prompts_count != num_frames_count:
            display_name = "ROOT" if prompts_key == "" else prompts_key
            mismatches.append(
                (display_name, prompts_count, links_count, num_frames_count)
            )

    if mismatches:
        console.print(f"[red]✗ Error: File count mismatch in subfolders[/red]\n")
        for subfolder, prompts_count, links_count, num_frames_count in mismatches:
            console.print(f"  {subfolder}:")
            console.print(f"    PROMPTS: {prompts_count} files")
            console.print(f"    LINKS: {links_count} files")
            console.print(f"    NUM_FRAMES: {num_frames_count} files")
        console.print(
            f"\nEach subfolder must have the same number of .txt files across all three folders."
        )
        sys.exit(1)


def validate_global_file_counts(
    prompts_structure: Dict[str, List[Path]],
    links_structure: Dict[str, List[Path]],
    num_frames_structure: Dict[str, List[Path]],
) -> None:
    """Validate that total .txt files match globally across all subfolders."""
    prompts_total = sum(len(files) for files in prompts_structure.values())
    links_total = sum(len(files) for files in links_structure.values())
    num_frames_total = sum(len(files) for files in num_frames_structure.values())

    if prompts_total != links_total or prompts_total != num_frames_total:
        console.print(f"[red]✗ Error: Global file count mismatch[/red]")
        console.print(f"  Total PROMPTS files: {prompts_total}")
        console.print(f"  Total LINKS files: {links_total}")
        console.print(f"  Total NUM_FRAMES files: {num_frames_total}")
        console.print(f"\nTotal file counts must match across all three folders.")
        sys.exit(1)


def validate_startup() -> Tuple[
    Dict[str, List[Path]], Dict[str, List[Path]], Dict[str, List[Path]]
]:
    """Run all startup validations, return subfolder structures or exit.

    Returns tuple of (prompts_structure, links_structure, num_frames_structure) dicts mapping
    relative subfolder paths to sorted .txt file lists.
    """
    console.print("[cyan]→ Starting validation...[/cyan]")
    validate_folders_exist()

    # Discover subfolder structures
    prompts_structure = discover_subfolder_structure(PROMPTS_DIR)
    links_structure = discover_subfolder_structure(LINKS_DIR)
    num_frames_structure = discover_subfolder_structure(NUM_FRAMES_DIR)

    # Check if any files found at all
    if not prompts_structure:
        console.print(f"[red]✗ Error: No .txt files found in {PROMPTS_DIR}[/red]")
        sys.exit(1)
    if not links_structure:
        console.print(f"[red]✗ Error: No .txt files found in {LINKS_DIR}[/red]")
        sys.exit(1)
    if not num_frames_structure:
        console.print(f"[red]✗ Error: No .txt files found in {NUM_FRAMES_DIR}[/red]")
        sys.exit(1)

    # Validate subfolder matching (case-insensitive)
    validate_subfolder_matching(
        prompts_structure, links_structure, num_frames_structure
    )

    # Validate no empty subfolders
    validate_empty_subfolders(prompts_structure, "PROMPTS")
    validate_empty_subfolders(links_structure, "LINKS")
    validate_empty_subfolders(num_frames_structure, "NUM_FRAMES")

    # Validate file counts per subfolder
    validate_per_subfolder_file_counts(
        prompts_structure, links_structure, num_frames_structure
    )

    # Validate global file counts
    validate_global_file_counts(
        prompts_structure, links_structure, num_frames_structure
    )

    # Calculate total pairs
    total_pairs = sum(len(files) for files in prompts_structure.values())
    console.print(f"[green]✓ Found {total_pairs} file triplets to process[/green]")

    # Log subfolder info
    num_subfolders = len(prompts_structure) - (1 if "" in prompts_structure else 0)
    if num_subfolders > 0:
        console.print(
            f"[green]✓ Detected {num_subfolders} matching subfolder(s)[/green]"
        )

    return prompts_structure, links_structure, num_frames_structure


def create_output_folder() -> Path:
    """Create timestamped output folder."""
    timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
    output_folder = OUTPUT_BASE / f"{timestamp}_IMG-TO-IMG-MD"
    output_folder.mkdir(parents=True, exist_ok=True)
    console.print(f"[green]✓ Created output folder: {output_folder.name}[/green]")
    return output_folder


def setup_logging(output_folder: Path) -> None:
    """Configure Loguru logger."""
    # Remove default handler to prevent console output
    logger.remove()
    # Add file-only handler
    logger.add(
        output_folder / "processing.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        level="DEBUG",
    )
    logger.info(f"Logging initialized")


def validate_url_format(url: str) -> None:
    """Validate URL format."""
    parsed = urlparse(url)
    if parsed.scheme not in ["http", "https"]:
        raise ValueError(f"Invalid URL scheme: {parsed.scheme}. Must be http or https.")


def validate_url_is_image(url: str) -> None:
    """Validate URL points to image."""
    extension = Path(urlparse(url).path).suffix.lower()
    if extension not in [".png", ".jpg", ".jpeg", ".gif", ".webp"]:
        raise ValueError(f"URL not an image. Extension: {extension}")


def validate_url_accessible(url: str) -> None:
    """Validate URL is reachable."""
    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
        if not (200 <= response.status_code < 300):
            raise requests.RequestException(f"Status code: {response.status_code}")
    except requests.Timeout:
        raise requests.RequestException("URL timed out after 5 seconds")
    except requests.RequestException as e:
        raise requests.RequestException(f"URL not accessible: {str(e)}")


def validate_url(url: str) -> None:
    """Run all URL validations."""
    validate_url_format(url)
    validate_url_is_image(url)
    validate_url_accessible(url)


def read_file_content(file_path: Path) -> str:
    """Read file, strip whitespace, raise if empty."""
    content = file_path.read_text(encoding="utf-8").strip()
    if not content:
        raise ValueError(f"File is empty: {file_path.name}")
    return content


def extract_image_filename(url: str) -> str:
    """Extract image filename from URL."""
    return Path(urlparse(url).path).name


def generate_markdown(prompt_text: str, image_url: str, num_frames: str) -> str:
    """Generate formatted markdown content."""
    return f"""{prompt_text}
{num_frames}
![image]({image_url})"""


def write_markdown_file(
    output_folder: Path, output_filename: str, content: str
) -> Path:
    """Write markdown to file."""
    output_path = output_folder / output_filename
    output_path.write_text(content, encoding="utf-8")
    return output_path


def create_failure_report(
    output_folder: Path,
    stage: str,
    prompts_file: Path,
    links_file: Path,
    num_frames_file: Path,
    error: Exception,
    subfolder_path: str = "",
) -> None:
    """Create FAILURE.md report with optional subfolder context."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tb = traceback.format_exc()

    subfolder_info = ""
    if subfolder_path:
        subfolder_info = f"\n**Subfolder**: {subfolder_path}"
    else:
        subfolder_info = "\n**Subfolder**: ROOT"

    failure_content = f"""# Processing Failure Report

**Timestamp**: {timestamp}
**Failed at**: {stage}{subfolder_info}
**File Triplet**: 
- PROMPTS file: {prompts_file.name}
- LINKS file: {links_file.name}
- NUM_FRAMES file: {num_frames_file.name}

## Error Details

{type(error).__name__}: {str(error)}

```
{tb}
```

## Root Cause

The processing failed during the {stage} stage for the file triplet listed above.

## Recommended Actions

1. Review the error details above to understand the specific issue
2. Check the content of all three input files:
   - {prompts_file}
   - {links_file}
   - {num_frames_file}
3. Verify the following:
   - PROMPTS file is not empty
   - LINKS file contains a valid image URL (http/https)
   - URL points to an accessible image file
   - NUM_FRAMES file contains a valid integer
   - All files are properly formatted text files
4. Fix the issue in the input files
5. Re-run the script with `python3 run.py`

## Files Processed Before Failure

Check processing.log for details on successfully processed file triplets before this failure occurred.
"""
    (output_folder / "FAILURE.md").write_text(failure_content, encoding="utf-8")
    console.print(f"[red]✗ FAILURE.md created[/red]")


def create_summary_report(
    output_folder: Path,
    total_pairs: int,
    success_count: int,
    start_time: float,
    generated_files: List[str],
    subfolder_stats: Optional[Dict[str, int]] = None,
) -> None:
    """Generate processing summary with optional subfolder breakdown."""
    elapsed_time = time.time() - start_time
    avg_time = elapsed_time / success_count if success_count > 0 else 0
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Group files by subfolder for display
    files_by_subfolder: Dict[str, List[str]] = {}
    for filepath in generated_files:
        if "/" in filepath:
            subfolder = filepath.rsplit("/", 1)[0]
            filename = filepath.rsplit("/", 1)[1]
        else:
            subfolder = "ROOT"
            filename = filepath

        if subfolder not in files_by_subfolder:
            files_by_subfolder[subfolder] = []
        files_by_subfolder[subfolder].append(filename)

    # Build files list grouped by subfolder
    files_list_parts = []
    for subfolder in natsorted(files_by_subfolder.keys()):
        files = files_by_subfolder[subfolder]
        files_list_parts.append(f"\n### {subfolder}\n")
        for filename in natsorted(files):
            files_list_parts.append(f"- `{filename}`")

    files_list = "\n".join(files_list_parts)

    # Build subfolder statistics if provided
    subfolder_breakdown = ""
    if subfolder_stats and len(subfolder_stats) > 1:
        subfolder_breakdown = "\n## Subfolder Breakdown\n\n"
        for subfolder in natsorted(subfolder_stats.keys()):
            display_name = "ROOT" if subfolder == "" else subfolder
            count = subfolder_stats[subfolder]
            subfolder_breakdown += f"- {display_name}: {count} file pairs\n"

    summary_content = f"""# Processing Summary

**Timestamp**: {timestamp}
**Total Pairs**: {total_pairs}
**Successfully Processed**: {success_count}
**Processing Time**: {elapsed_time:.2f} seconds
{subfolder_breakdown}
## Generated Files
{files_list}

## Statistics

- Average processing time per pair: {avg_time:.2f} seconds
- Total files read: {total_pairs * 2}
- Total markdown files generated: {success_count}

## Status

✓ All file pairs processed successfully!
"""
    (output_folder / "processing_summary.md").write_text(
        summary_content, encoding="utf-8"
    )
    logger.info(f"Summary report created")


def process_file_triplet(
    prompts_file: Path,
    links_file: Path,
    num_frames_file: Path,
    output_folder: Path,
    subfolder_path: str = "",
) -> str:
    """Process single file triplet, optionally within a subfolder structure.

    Args:
        prompts_file: Path to prompts .txt file
        links_file: Path to links .txt file
        num_frames_file: Path to num_frames .txt file
        output_folder: Base output folder
        subfolder_path: Relative subfolder path for output (empty string for root)

    Returns:
        Relative path to generated markdown file
    """
    logger.debug(f"Reading PROMPTS file: {prompts_file.name}")
    prompt_text = read_file_content(prompts_file)
    logger.debug(f"Reading LINKS file: {links_file.name}")
    image_url = read_file_content(links_file)
    logger.debug(f"Validating URL: {image_url}")
    validate_url(image_url)
    logger.debug(f"Reading NUM_FRAMES file: {num_frames_file.name}")
    num_frames = read_file_content(num_frames_file)
    logger.debug("Generating markdown content")
    markdown_content = generate_markdown(prompt_text, image_url, num_frames)

    # Create subfolder structure in output if needed
    actual_output_folder = output_folder
    if subfolder_path:
        actual_output_folder = output_folder / subfolder_path
        actual_output_folder.mkdir(parents=True, exist_ok=True)

    output_filename = f"{prompts_file.stem}.md"
    logger.debug(f"Writing markdown file: {output_filename}")
    write_markdown_file(actual_output_folder, output_filename, markdown_content)

    # Return relative path for tracking
    if subfolder_path:
        relative_output = f"{subfolder_path}/{output_filename}"
    else:
        relative_output = output_filename

    return relative_output


def main() -> None:
    """Main entry point."""
    console.print(
        "\n[bold cyan]═══════════════════════════════════════════[/bold cyan]"
    )
    console.print("[bold cyan]  IMG-TO-VID MARKDOWN ZIPPER[/bold cyan]")
    console.print(
        "[bold cyan]═══════════════════════════════════════════[/bold cyan]\n"
    )

    # Validate and get subfolder structures
    prompts_structure, links_structure, num_frames_structure = validate_startup()
    output_folder = create_output_folder()
    setup_logging(output_folder)

    start_time = time.time()
    success_count = 0
    generated_files: List[str] = []
    subfolder_stats: Dict[str, int] = {}

    # Build list of all file triplets across all subfolders
    # Use case-insensitive matching for subfolder keys
    prompts_keys_lower = {k.lower(): k for k in prompts_structure.keys()}
    links_keys_lower = {k.lower(): k for k in links_structure.keys()}
    num_frames_keys_lower = {k.lower(): k for k in num_frames_structure.keys()}

    all_triplets: List[Tuple[Path, Path, Path, str]] = []

    # Process subfolders in natural sort order (lowercase keys for matching)
    for key_lower in natsorted(prompts_keys_lower.keys()):
        prompts_key = prompts_keys_lower[key_lower]
        links_key = links_keys_lower[key_lower]
        num_frames_key = num_frames_keys_lower[key_lower]

        prompts_files = prompts_structure[prompts_key]
        links_files = links_structure[links_key]
        num_frames_files = num_frames_structure[num_frames_key]

        # Triplet files within this subfolder
        for prompts_file, links_file, num_frames_file in zip(
            prompts_files, links_files, num_frames_files
        ):
            all_triplets.append(
                (prompts_file, links_file, num_frames_file, prompts_key)
            )

        # Track stats per subfolder
        subfolder_stats[prompts_key] = len(prompts_files)

    total_triplets = len(all_triplets)
    console.print(f"\n[cyan]→ Processing {total_triplets} file triplets...[/cyan]\n")

    # Process all triplets with progress bar
    with alive_bar(
        total_triplets,
        title="Processing File Triplets",
        dual_line=True,
        bar="smooth",
        spinner="dots_waves",
        unit="triplets",
    ) as bar:
        for prompts_file, links_file, num_frames_file, subfolder_path in all_triplets:
            try:
                display_path = subfolder_path if subfolder_path else "ROOT"

                # Update progress bar text with current file
                bar.text = (
                    f"→ Processing: {prompts_file.stem}\n  Subfolder: {display_path}"
                )

                # Log subfolder transitions
                if success_count == 0 or (
                    success_count > 0
                    and all_triplets[success_count - 1][3] != subfolder_path
                ):
                    logger.info(f"Processing subfolder: {display_path}")

                output_filename = process_file_triplet(
                    prompts_file,
                    links_file,
                    num_frames_file,
                    output_folder,
                    subfolder_path,
                )
                success_count += 1
                generated_files.append(output_filename)

                # Update bar text with completion status
                bar.text = (
                    f"✓ Generated: {prompts_file.stem}.md\n  Subfolder: {display_path}"
                )
                bar()
            except Exception as e:
                logger.error(f"Processing failed: {str(e)}")
                console.print(f"\n[red]✗ Processing failed for triplet:[/red]")
                console.print(f"  PROMPTS: {prompts_file.name}")
                console.print(f"  LINKS: {links_file.name}")
                console.print(f"  NUM_FRAMES: {num_frames_file.name}")
                console.print(
                    f"  Subfolder: {subfolder_path if subfolder_path else 'ROOT'}"
                )
                console.print(f"  Error: {str(e)}\n")
                create_failure_report(
                    output_folder,
                    "File Processing",
                    prompts_file,
                    links_file,
                    num_frames_file,
                    e,
                    subfolder_path,
                )
                sys.exit(1)

    create_summary_report(
        output_folder,
        total_triplets,
        success_count,
        start_time,
        generated_files,
        subfolder_stats,
    )
    elapsed = time.time() - start_time
    console.print(f"\n[bold green]✓ Processing complete![/bold green]")
    console.print(
        f"  Generated {success_count} markdown files in {elapsed:.2f} seconds"
    )
    console.print(f"  Output folder: {output_folder.name}\n")
    logger.info(f"Processing complete: {success_count}/{total_triplets} files")


if __name__ == "__main__":
    main()
