# Image-to-Markdown Pairing Script

A lightweight Python script that pairs text prompts, image URLs, and num_frames values from separate input folders and generates structured Markdown files.

## Features

- **Triple-folder input processing**: Read prompts, image URLs, and num_frames from three separate folders
- **Natural sort pairing**: Files paired by natsort position (1st with 1st, 2nd with 2nd)
- **URL validation**: Three-stage validation (format, image extension, accessibility)
- **Fail-fast error handling**: Stop immediately on errors with detailed FAILURE.md reports
- **Progress tracking**: Beautiful progress bars with alive-progress and Rich console output
- **Dual logging**: Technical Loguru logs and human-readable Markdown summaries

## Quick Start

```bash
# Zero-setup execution - handles venv creation and dependencies automatically
python3 run.py
```

That's it! The `run.py` wrapper handles:
- Virtual environment creation (if needed)
- Dependency installation/updates
- Running the main script

## Input Structure

Place your files in these folders:

```
USER-FILES/04.INPUT/
├── 04.1_PROMPTS/       # .txt files with prompt text (one per file)
├── 04.2_NUM_FRAMES/    # .txt files with num_frames integers (one per file)
└── 04.3_LINKS/         # .txt files with image URLs (one per file)
```

**Requirements:**
- Equal number of `.txt` files in all three folders
- Files paired by natsort order (NOT by filename matching)
- Non-.txt files are ignored
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

## Generated Markdown Format

Each markdown file follows this structure:

```markdown
Your prompt text here.
240
![image](https://example.com/path/to/image.png)
```

## Error Handling

The script follows a **fail-fast philosophy**:

- **Startup failures** (before output folder creation):
  - Missing input folders
  - No .txt files found
  - File count mismatch between PROMPTS, LINKS, and NUM_FRAMES

- **Processing failures** (after output folder creation):
  - Empty .txt file
  - Invalid URL format
  - URL not pointing to image
  - URL not accessible
  - Any other processing error

All failures create a detailed `FAILURE.md` report with:
- Error description and traceback
- File triplet that caused the failure
- Recommended fix actions

## Example Usage

1. **Prepare input files:**
   ```bash
   # Create PROMPTS files (one prompt per file)
   echo "A beautiful sunset" > USER-FILES/04.INPUT/04.1_PROMPTS/frame001.txt
   echo "A mountain landscape" > USER-FILES/04.INPUT/04.1_PROMPTS/frame002.txt
   
   # Create NUM_FRAMES files (one integer per file)
   echo "240" > USER-FILES/04.INPUT/04.2_NUM_FRAMES/frame001.txt
   echo "180" > USER-FILES/04.INPUT/04.2_NUM_FRAMES/frame002.txt
   
   # Create LINKS files (one URL per file)
   echo "https://example.com/image1.png" > USER-FILES/04.INPUT/04.3_LINKS/frame001.txt
   echo "https://example.com/image2.png" > USER-FILES/04.INPUT/04.3_LINKS/frame002.txt
   ```

2. **Run the script:**
   ```bash
   python3 run.py
   ```

3. **Check output:**
   ```bash
   # View generated files
   ls USER-FILES/05.OUTPUT/*/
   
   # Read summary report
   cat USER-FILES/05.OUTPUT/*/processing_summary.md
   ```

## Troubleshooting

**Error: File count mismatch**
- Ensure equal number of .txt files in all three folders (PROMPTS, LINKS, NUM_FRAMES)
- Only .txt files are counted (other files are ignored)

**Error: Invalid URL format**
- Check LINKS file contains valid HTTP/HTTPS URL
- URL must start with `http://` or `https://`

**Error: URL not accessible**
- Verify URL is reachable (check network connection)
- Check URL returns 2xx status code

**Error: URL not an image**
- Ensure URL ends with image extension (.png, .jpg, .jpeg, .gif, .webp)

**Error: Empty file**
- Ensure all .txt files have content
- Files with only whitespace are considered empty

## Technical Details

- **Language**: Python 3.8+
- **Dependencies**: loguru, natsort, rich, alive-progress, requests
- **Code style**: Type hints, pathlib, fail-fast error handling
- **File size**: ~677 lines (single file implementation)
- **Performance**: ~0.25s per file triplet (includes URL validation)

## Project Structure

```
img-to-vid-zipper/
├── src/
│   └── main.py              # Main script (~677 lines)
├── USER-FILES/
│   ├── 04.INPUT/
│   │   ├── 04.1_PROMPTS/    # Prompt text files
│   │   ├── 04.2_NUM_FRAMES/ # Num frames integer files
│   │   └── 04.3_LINKS/      # Image URL files
│   └── 05.OUTPUT/           # Timestamped output folders
├── run.py                   # Environment setup wrapper
├── requirements.txt         # Pinned dependencies
├── .gitignore              # VCS exclusions
└── README.md               # This file
```

## Philosophy

This script follows a minimalist philosophy:
- One tool, one purpose
- Fail fast with clear error messages
- No silent failures
- Sequential processing (deterministic)
- No premature abstractions
- Simple, boring code that works

## Manual Entry Point

If you prefer manual control:

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the script
python3 -m src.main
```

## License

Personal tool - no license, no warranty, no support.
