# Image-to-Video Markdown Zipper

A lightweight Python script that pairs text prompts, image URLs, and num_frames values from three separate input folders and generates structured Markdown files with one image per file.

## Features

- **Triple-folder input processing**: Read prompts, image URLs, and num_frames from three folders
- **Natural sort pairing**: Files paired by natsort position (1st with 1st, 2nd with 2nd)
- **Nested subfolder support**: Unlimited-depth subfolder trees with case-insensitive matching
- **URL validation**: Three-stage validation (format, image extension, accessibility)
- **Fail-fast error handling**: Stop immediately on errors with detailed FAILURE.md reports
- **Progress tracking**: alive-progress dual-line bars with Rich console output
- **Dual logging**: Loguru technical logs + human-readable Markdown summaries

## Quick Start

```bash
python3 run.py
```

The `run.py` wrapper handles venv creation, dependency installation, and script execution.

## Input Structure

```
USER-FILES/04.INPUT/
├── 04.1_PROMPTS/       # .txt files with prompt text (one per file)
├── 04.2_NUM_FRAMES/    # .txt files with num_frames integers (one per file)
└── 04.3_IMG_LINKS/     # .txt files with image URLs (one per file)
```

**Requirements:**
- Equal number of `.txt` files in all three folders
- Files paired by natsort order (NOT by filename matching)
- Subfolders must match across all three directories (case-insensitive)
- URLs must be valid HTTP/HTTPS pointing to image files
- Files cannot be empty

## Output Structure

```
USER-FILES/05.OUTPUT/YYMMDD_HHMMSS_IMG-TO-IMG-MD/
├── link001.md              # Generated markdown files
├── link002.md
├── ...
├── processing_summary.md   # Human-readable summary
├── processing.log          # Technical log (Loguru)
└── FAILURE.md              # Error report (if processing fails)
```

Subfolder structures from input are mirrored in the output.

## Generated Markdown Format

```markdown
Your prompt text here.
240
![image](https://example.com/path/to/image.png)
```

## Error Handling

Fail-fast philosophy: any error immediately stops processing and creates a `FAILURE.md` with traceback, file triplet details, and recommended fixes.

- **Startup failures**: missing folders, no files found, subfolder mismatches, file count mismatches
- **Processing failures**: empty files, invalid/not-image/inaccessible URLs, any exception

## Dead Code Note

`validate_file_counts()` and `discover_txt_files()` are present in the source but unused. They are legacy flat-discovery functions superseded by the recursive `discover_subfolder_structure()` and per-subfolder validation variants.

## Project Structure

```
img-to-vid-zipper/
├── src/
│   └── main.py              # Main script (~685 lines)
├── USER-FILES/
│   ├── 04.INPUT/
│   │   ├── 04.1_PROMPTS/    # Prompt text files
│   │   ├── 04.2_NUM_FRAMES/ # Num frames integer files
│   │   └── 04.3_IMG_LINKS/  # Image URL files
│   └── 05.OUTPUT/           # Timestamped output folders
├── run.py                   # Environment setup wrapper
├── requirements.txt         # Pinned dependencies
├── .gitignore
└── README.md
```

## Technical Details

- **Language**: Python 3.8+
- **Dependencies**: loguru, natsort, rich, alive-progress, requests
- **Code style**: Type hints, pathlib, fail-fast error handling
- **Performance**: ~0.25s per file triplet (includes URL validation)

## Manual Entry Point

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python3 -m src.main
```
