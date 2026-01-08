# PRD: Image-to-Markdown Pairing Script

## 01. Project Definition

### 01.1 Project Description

A lightweight Python script that pairs image URLs with text prompts from separate input folders and generates structured Markdown files. The script reads `.txt` files containing image URLs from one folder and matching `.txt` files containing prompt text from another folder, then creates formatted Markdown documents embedding the images and displaying the prompts in code blocks.

### 01.2 Core Features

- **Dual-folder input processing**: Read image URLs from `04.INPUT/04.1.LINKS/` and prompt text from `04.INPUT/04.2_PROMPTS/`
- **Natural sort pairing**: Pair files from both folders by natsort position (1st with 1st, 2nd with 2nd, etc.)
- **File count validation**: Verify matching number of `.txt` files in both folders before processing
- **Markdown generation**: Create formatted `.md` files with embedded images and code-blocked prompts
- **Timestamped output**: Generate outputs in `05.OUTPUT/YYMMDD_HHMMSS_IMG-TO-IMG-MD/` folder
- **URL validation**: Validate image URLs for proper format and accessibility
- **Fail-fast error handling**: Stop immediately on any error with detailed FAILURE.md report
- **Progress tracking**: Display comprehensive progress using alive-progress and Rich
- **Dual logging**: Technical Loguru logs and human-readable Markdown summary reports

### 01.3 Specific Requirements

**Input Requirements**
- Accept only `.txt` files from input folders
- Ignore all non-`.txt` files (`.md`, `.json`, `.png`, etc.)
- Require exact count match between LINKS and PROMPTS folders
- Strip leading/trailing whitespace from URLs and prompt text
- Fail immediately on empty `.txt` files

**URL Validation Requirements**
- Validate URL format (must be valid HTTP/HTTPS URL)
- Validate URL points to an image (check file extension: `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`)
- Verify URL is accessible (perform HTTP HEAD request)
- Support any image hosting platform (not limited to Backblaze B2)

**Output Requirements**
- Name output `.md` files using LINKS `.txt` filename (e.g., `link001.txt` → `link001.md`)
- Use flat structure (all `.md` files directly in timestamped output folder)
- Include image filename extracted from URL in headers and labels
- Display PROMPTS `.txt` filename in "TEXT SOURCE" label
- Generate processing summary in Markdown format
- Create technical Loguru logs for debugging

**Error Handling Requirements**
- Fail immediately at startup if `.txt` file counts don't match (before creating output folder)
- Fail immediately if any file pair has validation errors (empty file, invalid URL, unreachable URL)
- Create FAILURE.md at script run level in output folder
- Do NOT create output folder if validation fails at startup
- Include full error context and actionable solutions in FAILURE.md

### 01.4 Project Context

**Option A: Personal Tool (LLM-Operated)**

- **Users**: Just me (developer/owner)
- **Operation**: Claude Code or other LLM operates on my behalf
- **Documentation**: LLM-readable (clear docstrings and comments)
- **Testing**: I test manually myself - no automated tests, no test frameworks, no test suites
- **CI/CD**: Not needed (no team, no external deployment)
- **Simplification Impact**:
  - No user documentation needed
  - No automated testing whatsoever
  - No test files or test directories
  - No release management
  - No external integrations
  - Focus exclusively on building functional scripts

### 01.5 Error Handling Strategy

**Fail-Fast Philosophy**

All errors result in immediate script termination with detailed FAILURE.md report.

**Startup Validation Failures (Before Output Folder Creation)**
- **Missing input folders**: Exit with error message, no output folder created
- **No .txt files found**: Exit with error message, no output folder created
- **File count mismatch**: Exit with error message, no output folder created
- **Action**: Log error to console, display actionable message, exit with code 1

**Processing Failures (After Output Folder Creation)**
- **Empty .txt file**: Create FAILURE.md, exit immediately
- **Invalid URL format**: Create FAILURE.md, exit immediately
- **URL not accessible**: Create FAILURE.md, exit immediately
- **URL not an image**: Create FAILURE.md, exit immediately
- **Markdown generation error**: Create FAILURE.md, exit immediately
- **Action**: Create FAILURE.md in `05.OUTPUT/YYMMDD_HHMMSS_IMG-TO-IMG-MD/FAILURE.md` with:
  - Error type and description
  - Which file pair caused the failure
  - Full error traceback
  - Actionable solution steps
  - Timestamp of failure

**FAILURE.md Format**
```markdown
# Processing Failure Report

**Timestamp**: YYYY-MM-DD HH:MM:SS
**Failed at**: [Stage - e.g., "URL Validation", "Markdown Generation"]
**File Pair**: 
- LINKS file: [filename]
- PROMPTS file: [filename]

## Error Details

[Detailed error message and traceback]

## Root Cause

[Clear explanation of what went wrong]

## Recommended Actions

1. [Specific step to fix the issue]
2. [Additional steps if needed]
3. [Verification steps]

## Files Processed Before Failure

Successfully generated: X of Y markdown files

[List of successfully generated files if any]
```

---

## 02. Minimalist Architecture Philosophy

### Core Principles

**Simplicity First**

- One purpose per file
- Self-documenting variable names
- Standard patterns only
- Functions under 50 lines
- No premature abstractions
- No custom frameworks
- Use established libraries over custom code

### Python Implementation Standards

**Code Structure**

- Type hints for all functions
- pathlib.Path for file operations
- Single file implementation (`src/main.py`)
- Functions under 50 lines
- Target: Under 250 lines total

**Error Handling**

- Custom exceptions with clear messages
- Fail fast with actionable errors
- Stop processing on first failure
- Structured logging with Loguru
- Detailed FAILURE.md reports

**Dependencies**

- Pin exact versions in requirements.txt
- Use standard library when sufficient
- Popular libraries (natsort, loguru, rich, alive-progress) over custom code
- Virtual environment isolation

**File Processing**

- Show comprehensive progress for operations
- Process files sequentially (natsort order)
- Validate all inputs before processing
- Handle encoding issues gracefully
- Strip whitespace from input content

**Testing & Documentation**

For Personal Tools (Option A):

- Build functional scripts - I test them manually myself
- No automated tests, no test frameworks, no test files
- LLM-readable docstrings in all functions
- Clear inline comments for complex logic
- No .env files needed (no configuration)

---

## 03. Dependencies

### Required Python Packages

```txt
# Core dependencies
loguru==0.7.2           # Structured logging
natsort==8.4.0          # Natural sorting for file pairing
rich==13.7.0            # Console output and logging
alive-progress==3.1.5   # Progress bar with visual flair
requests==2.31.0        # URL validation and accessibility checks

# Standard library (no installation needed)
pathlib                 # File operations
sys                     # Exit codes
datetime                # Timestamps
```

### Folder Structure

```plaintext
img-to-img-zipper/
├── src/                           # Source code
│   └── main.py                    # Main entry point
├── .env.example                   # Not needed for this project
├── .gitignore                     # Git exclusions
├── requirements.txt               # Python dependencies
├── run.py                         # Environment setup wrapper
├── README.md                      # Project documentation
└── USER-FILES/                    # Data processing folders
    ├── 00.KB/                     # Knowledge base
    │   ├── idea_brief.md
    │   ├── prd.md
    │   └── code_manifesto_memo.md
    ├── 01.CONFIG/                 # Not used for this project
    ├── 02.STANDBY/                # Files ready for processing
    ├── 03.PROFILES/               # Not used for this project
    ├── 04.INPUT/                  # Active input (READ ONLY)
    │   ├── 04.1.LINKS/            # .txt files with image URLs
    │   └── 04.2_PROMPTS/          # .txt files with prompt text
    ├── 05.OUTPUT/                 # Generated outputs (WRITE ONLY)
    │   └── YYMMDD_HHMMSS_IMG-TO-IMG-MD/
    │       ├── link001.md
    │       ├── link002.md
    │       ├── processing_summary.md
    │       ├── processing.log
    │       └── FAILURE.md (if errors occur)
    ├── 06.DONE/                   # Processed files archive
    └── 07.TEMP/                   # Temporary files
        ├── example1.md
        └── prd_questions.md
```

---

## 04. Input/Output Pattern for Batch Processing Projects

### 04.1 Purpose and Scope

This script follows the standard batch processing pattern for personal tools. Users organize data files in designated input folders, and the script processes them according to established conventions.

**Key principle**: Users manage data organization; scripts follow folder conventions

### 04.2 Input Folder Structure

```plaintext
USER-FILES/04.INPUT/
├── 04.1.LINKS/              # Image URL files
│   ├── link001.txt          # Contains single image URL
│   ├── link002.txt          # Contains single image URL
│   ├── link003.txt          # Contains single image URL
│   └── other_file.md        # IGNORED (not .txt)
└── 04.2_PROMPTS/            # Prompt text files
    ├── prompt001.txt        # Contains prompt text
    ├── prompt002.txt        # Contains prompt text
    ├── prompt003.txt        # Contains prompt text
    └── notes.json           # IGNORED (not .txt)
```

**Input File Requirements**

- **LINKS files**: Each `.txt` file contains one image URL (HTTP/HTTPS)
- **PROMPTS files**: Each `.txt` file contains prompt text (any length)
- **Pairing**: Files paired by natsort position (1st LINKS ↔ 1st PROMPTS)
- **Validation**: Must have equal count of `.txt` files in both folders
- **Ignored files**: All non-`.txt` files are ignored
- **Content processing**: Leading/trailing whitespace stripped from URLs and prompts

### 04.3 Output Folder Structure

```plaintext
USER-FILES/05.OUTPUT/
└── YYMMDD_HHMMSS_IMG-TO-IMG-MD/     # Timestamped output folder
    ├── link001.md                    # Generated markdown file
    ├── link002.md                    # Generated markdown file
    ├── link003.md                    # Generated markdown file
    ├── processing_summary.md         # Human-readable summary
    ├── processing.log                # Technical Loguru log
    └── FAILURE.md                    # Created only if processing fails
```

**Output Folder Naming**

- **Format**: `YYMMDD_HHMMSS_IMG-TO-IMG-MD` (e.g., `250131_143022_IMG-TO-IMG-MD`)
- **Descriptive suffix**: `_IMG-TO-IMG-MD` identifies this specific tool's output
- **Creation timing**: Only created after all startup validations pass
- **No creation on startup failures**: If file count mismatch or missing folders, no output folder created

**Output File Naming**

- **Markdown files**: Named using LINKS `.txt` filename (e.g., `link001.txt` → `link001.md`)
- **Summary report**: `processing_summary.md` (human-readable)
- **Technical log**: `processing.log` (Loguru format)
- **Failure report**: `FAILURE.md` (only created on errors)

### 04.4 Processing Flow Diagrams

#### Overall Processing Flow

```plaintext
[Startup Validation]
    ↓
[Check folders exist] → NO → [Exit with error]
    ↓ YES
[Count .txt files in both folders] → MISMATCH → [Exit with error]
    ↓ MATCH
[Create output folder: YYMMDD_HHMMSS_IMG-TO-IMG-MD]
    ↓
[Discover .txt files in natsort order]
    ↓
[Pair files: 1st LINKS ↔ 1st PROMPTS, etc.]
    ↓
[For each pair sequentially]
    ↓
[Read LINKS file] → EMPTY → [Create FAILURE.md, Exit]
    ↓ HAS CONTENT
[Validate URL format] → INVALID → [Create FAILURE.md, Exit]
    ↓ VALID
[Validate URL accessibility] → UNREACHABLE → [Create FAILURE.md, Exit]
    ↓ REACHABLE
[Read PROMPTS file] → EMPTY → [Create FAILURE.md, Exit]
    ↓ HAS CONTENT
[Generate Markdown file]
    ↓
[Save to output folder]
    ↓
[Next pair or Complete]
    ↓
[Generate processing_summary.md]
    ↓
[Complete successfully]
```

#### File Pairing Logic

```plaintext
04.1.LINKS/          04.2_PROMPTS/        Output/
-----------          --------------        -------
link001.txt    ←→    prompt001.txt   →    link001.md
link002.txt    ←→    prompt002.txt   →    link002.md
link003.txt    ←→    prompt003.txt   →    link003.md
                     
Pairing: By natsort position (NOT by filename matching)
```

### 04.5 User Workflow

#### Standard Processing Flow

1. **Prepare Files**: Create `.txt` files in both input folders
   - Place image URLs (one per file) in `04.INPUT/04.1.LINKS/`
   - Place prompt text (one per file) in `04.INPUT/04.2_PROMPTS/`
   - Ensure equal number of `.txt` files in both folders

2. **Run Script**: Execute `python3 run.py`
   - Script validates folder structure
   - Script counts `.txt` files
   - Script creates timestamped output folder
   - Script processes pairs sequentially
   - Script shows progress with alive-progress and Rich

3. **Check Output**: Review results in `05.OUTPUT/YYMMDD_HHMMSS_IMG-TO-IMG-MD/`
   - Check generated `.md` files
   - Review `processing_summary.md` for overview
   - Check `processing.log` for technical details
   - If errors occurred, review `FAILURE.md`

4. **Archive**: Move processed files from `04.INPUT/` to `06.DONE/`
   - Manual step - script never moves input files
   - User controls archival timing and organization

### 04.6 Markdown File Template

Each generated Markdown file follows this structure (based on provided example, with HTML comments removed):

```markdown
---

# [IMAGE_FILENAME_FROM_URL]

| IMAGE SOURCE: [IMAGE_FILENAME_FROM_URL]                     |
| ------------------------------------------------------------ |
| ![image]([FULL_IMAGE_URL_FROM_LINKS_FILE])                   |

**TEXT SOURCE: [PROMPTS_TXT_FILENAME]:**

```text
[PROMPT_TEXT_FROM_PROMPTS_FILE]
```

---
```

**Example Output**

If `04.1.LINKS/link001.txt` contains:
```
https://f003.backblazeb2.com/file/isof-bucket/batch6_upscaled/prompt09.0.png
```

And `04.2_PROMPTS/prompt001.txt` contains:
```
A man carries heavy bags on a ship dock.
```

Then `05.OUTPUT/250131_143022_IMG-TO-IMG-MD/link001.md` will contain:

```markdown
---

# prompt09.0.png

| IMAGE SOURCE: prompt09.0.png                                                           |
| -------------------------------------------------------------------------------------- |
| ![image](https://f003.backblazeb2.com/file/isof-bucket/batch6_upscaled/prompt09.0.png) |

**TEXT SOURCE: prompt001.txt:**

```text
A man carries heavy bags on a ship dock.
```

---
```

**Template Variables**

- `[IMAGE_FILENAME_FROM_URL]`: Extracted from URL path (e.g., `prompt09.0.png`)
- `[FULL_IMAGE_URL_FROM_LINKS_FILE]`: Full URL from LINKS .txt file
- `[PROMPTS_TXT_FILENAME]`: Filename of PROMPTS .txt file (e.g., `prompt001.txt`)
- `[PROMPT_TEXT_FROM_PROMPTS_FILE]`: Content from PROMPTS .txt file (whitespace stripped)

### 04.7 Configuration Management

**No Configuration Required**

This script is intentionally simple and requires no configuration files.

- No `01.CONFIG/config.json` needed
- No `03.PROFILES/profile.yaml` needed
- No environment variables needed
- All behavior is hardcoded according to specifications

### 04.8 Output Organization

**Flat Structure**

All generated files are placed directly in the timestamped output folder:

```plaintext
05.OUTPUT/250131_143022_IMG-TO-IMG-MD/
├── link001.md                    # Generated markdown
├── link002.md                    # Generated markdown
├── link003.md                    # Generated markdown
├── processing_summary.md         # Summary report
├── processing.log                # Technical log
└── FAILURE.md                    # Error report (if applicable)
```

**No per-file subfolders** - simpler structure for this use case.

### 04.9 Key Principles

#### Data Organization

- Users control where files are placed
- Scripts follow the established folder conventions
- Clear separation between LINKS and PROMPTS input folders
- Output isolated in timestamped folders

#### Processing Safety

- Original files are never modified
- Original files are never moved
- All outputs are generated in timestamped folders
- Failed processing creates detailed FAILURE.md

#### Sequential Processing

- Files processed in natsort order
- Deterministic and predictable
- No parallel processing
- Easy to track and debug

### 04.10 Implementation Details

#### Logging Strategy

**Dual Logging Approach**

1. **Technical Log (Loguru)** - `processing.log`
   - All script operations
   - Validation steps
   - URL checks
   - File reads/writes
   - Timestamps for all operations
   - Full error tracebacks

2. **Summary Report (Markdown)** - `processing_summary.md`
   - Human-readable overview
   - Total files processed
   - Success count
   - Processing time
   - List of generated files
   - High-level status

**Console Output (Rich)**

- Success messages in green
- Error messages in red
- File operations in cyan
- Validation steps in yellow

**Progress Display (alive-progress)**

- Main progress bar showing X of Y pairs processed
- Current file being processed in dual-line mode
- Current phase (Reading LINKS, Validating URL, Reading PROMPTS, Generating MD)
- Processing rate (pairs/second)
- ETA to completion

#### File Naming and Organization

**Input Preservation**: Original files never modified or moved.

**Timestamped Outputs**: Format `YYMMDD_HHMMSS_IMG-TO-IMG-MD` prevents overwrites.

**Output Directory Naming**: `YYMMDD_HHMMSS_IMG-TO-IMG-MD` with descriptive suffix for this tool.

**File Naming**: Uses LINKS .txt filename as base (e.g., `link001.txt` → `link001.md`).

#### Error Handling and Recovery

**No Recovery - Fail Fast**

- First error stops all processing
- Detailed FAILURE.md created
- No partial processing
- User fixes issue and re-runs script

**Clear Error Reporting**

- Both machine-readable (Loguru) and human-readable (FAILURE.md) logs
- Specific file pair that caused failure
- Actionable solution steps

#### Processing Modes

**Single Mode: Transformation**

- Process according to specifications
- Output to timestamped folder
- No analysis-only mode
- No dry-run mode

#### Technical Implementation

**Script Flow**: 
1. Validate folders exist
2. Count .txt files (must match)
3. Create output folder
4. Discover files in natsort order
5. Pair files by position
6. Process each pair sequentially
7. Generate summary report

**File Formats**: 
- INPUT: `.txt` files only
- OUTPUT: `.md` files + `.log` + `processing_summary.md`

**Logging**: 
- Loguru (technical) + Markdown (summaries) + Rich (console)

**Error Handling**: 
- Fail fast, detailed logs, FAILURE.md report

**Performance**: 
- Sequential processing
- Progress reporting with alive-progress
- Memory efficient (one pair at a time)

### 04.11 Version Control Guidelines

#### Directory Exclusion (.gitignore)

```gitignore
# Virtual environment
venv/
.venv/
env/

# Python cache
__pycache__/
*.pyc
*.pyo

# User data folders
USER-FILES/04.INPUT/
USER-FILES/05.OUTPUT/
USER-FILES/06.DONE/
USER-FILES/07.TEMP/

# Logs
*.log

# OS files
.DS_Store
Thumbs.db
```

#### Rationale for Exclusion

1. **Repository Size Management**: Input/output files may be numerous and large
2. **Data Privacy**: Input files may contain sensitive URLs or prompts
3. **Reproducibility**: Output files are regenerated each run
4. **Focus on Code**: Version control focuses on processing logic, not data

**Data Management**

- Never commit input data
- Never commit output files
- Document input format in README
- Use .gitkeep files in empty directories
- Include USER-FILES structure in documentation

**Project Structure**

- Maintain folder structure even when empty
- Use .gitkeep files in empty directories
- Document the pattern in README
- Include setup instructions for new users

#### Security Considerations

**No Sensitive Data**

- No API keys required
- No credentials needed
- URLs are public image links
- Prompts are user-generated text

**Data Privacy**

- Review input files before sharing
- URLs may point to private/proprietary images
- Prompts may contain sensitive information
- Never commit USER-FILES/04.INPUT/ or 05.OUTPUT/

#### How to Run the Script

**Main entry point**: `python3 -m src.main` (with venv activated)

**Wrapper script**: `python3 run.py` handles complete environment setup:
- Creates virtual environment if it doesn't exist
- Activates the virtual environment
- Installs/updates dependencies from requirements.txt
- Runs the main entry point

**Usage**: `python3 run.py` - zero manual steps required

---

## 05. Technical Specifications

### 05.1 Input File Format

**LINKS Files (04.1.LINKS/*.txt)**

- **Content**: Single image URL per file
- **Format**: Plain text, one line
- **Validation**: 
  - Must be valid HTTP/HTTPS URL
  - Must point to image file (.png, .jpg, .jpeg, .gif, .webp)
  - Must be accessible (HTTP HEAD request succeeds)
- **Processing**: Strip leading/trailing whitespace

**Example LINKS File**
```
https://f003.backblazeb2.com/file/isof-bucket/batch6_upscaled/prompt09.0.png
```

**PROMPTS Files (04.2_PROMPTS/*.txt)**

- **Content**: Prompt text (any length)
- **Format**: Plain text, single or multi-line
- **Validation**: Must not be empty
- **Processing**: Strip leading/trailing whitespace

**Example PROMPTS File**
```
A man carries heavy bags on a ship dock.
```

### 05.2 URL Validation Logic

**Three-Stage Validation**

1. **Format Validation**
   - Check URL has valid scheme (http or https)
   - Check URL has valid structure
   - Use `urllib.parse` for validation

2. **Image Extension Validation**
   - Extract filename from URL path
   - Check extension is in allowed list: `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`
   - Case-insensitive check

3. **Accessibility Validation**
   - Perform HTTP HEAD request to URL
   - Check response status code is 2xx
   - Set reasonable timeout (5 seconds)
   - Handle network errors gracefully

**Validation Failure Actions**

- **Format invalid**: Fail immediately, create FAILURE.md with "Invalid URL format"
- **Not an image**: Fail immediately, create FAILURE.md with "URL does not point to image file"
- **Not accessible**: Fail immediately, create FAILURE.md with "URL not accessible" + HTTP status code

### 05.3 Markdown Generation Logic

**Template Structure**

```markdown
---

# {image_filename}

| IMAGE SOURCE: {image_filename}                 |
| ---------------------------------------------- |
| ![image]({full_image_url})                     |

**TEXT SOURCE: {prompts_txt_filename}:**

```text
{prompt_text}
```

---
```

**Variable Extraction**

- `{image_filename}`: Extracted from URL path using `pathlib.Path(urlparse(url).path).name`
- `{full_image_url}`: Full URL from LINKS .txt file (whitespace stripped)
- `{prompts_txt_filename}`: Filename of PROMPTS .txt file (e.g., `prompt001.txt`)
- `{prompt_text}`: Content from PROMPTS .txt file (whitespace stripped)

### 05.4 Progress Bar Implementation

**alive-progress Configuration**

```python
from alive_progress import alive_bar

with alive_bar(
    total=len(file_pairs),
    title='Processing File Pairs',
    dual_line=True,  # Put detailed text below bar
    bar='smooth',
    spinner='dots_waves',
    unit='pairs',
) as bar:
    for pair in file_pairs:
        bar.text = f'→ Processing: {pair.links_file}\nPhase: {current_phase}'
        # Process the pair
        bar()  # Increment progress
```

**Rich Integration**

```python
from rich.console import Console

console = Console()

# Success logging
console.print(f"[green]✓[/green] Generated {output_file}")

# Error logging
console.print(f"[red]✗ Failed: {error_message}[/red]")

# Info logging
console.print(f"[cyan]→ Validating URL: {url}[/cyan]")
```

**Progress Display Details**

- Overall progress bar (X of Y pairs)
- Current LINKS file being processed (dual-line mode)
- Current processing phase (Reading, Validating, Generating)
- Processing rate (pairs/second)
- ETA to completion
- Success/error messages logged with Rich

### 05.5 Logging Implementation

**Loguru Configuration**

```python
from loguru import logger

# Configure logger to write to output folder
logger.add(
    output_folder / "processing.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    level="DEBUG",
)

# Log all operations
logger.info(f"Discovered {len(links_files)} LINKS files")
logger.debug(f"Reading file: {links_file}")
logger.error(f"URL validation failed: {url} - {error}")
```

**Summary Report Template (processing_summary.md)**

```markdown
# Processing Summary

**Timestamp**: {timestamp}
**Total Pairs**: {total_pairs}
**Successfully Processed**: {success_count}
**Processing Time**: {elapsed_time} seconds

## Generated Files

- `{output_file_1}`
- `{output_file_2}`
- ...

## Statistics

- Average processing time per pair: {avg_time} seconds
- Total files read: {total_files_read}
- Total markdown files generated: {total_md_generated}

## Status

{success_message or failure_message}
```

### 05.6 Error Scenarios and Responses

| Error Scenario | Detection Point | Response |
|---------------|----------------|----------|
| LINKS folder missing | Startup validation | Exit immediately, console error, no output folder |
| PROMPTS folder missing | Startup validation | Exit immediately, console error, no output folder |
| No .txt files in LINKS | Startup validation | Exit immediately, console error, no output folder |
| No .txt files in PROMPTS | Startup validation | Exit immediately, console error, no output folder |
| File count mismatch | Startup validation | Exit immediately, console error, no output folder |
| Empty LINKS file | File reading | Create FAILURE.md, exit immediately |
| Empty PROMPTS file | File reading | Create FAILURE.md, exit immediately |
| Invalid URL format | URL validation | Create FAILURE.md, exit immediately |
| URL not an image | URL validation | Create FAILURE.md, exit immediately |
| URL not accessible | URL validation | Create FAILURE.md, exit immediately |
| Markdown write error | File writing | Create FAILURE.md, exit immediately |

### 05.7 File Size Constraints

**Code Organization**

- Single file implementation: `src/main.py`
- Target: Under 250 lines total
- All logic in one module for simplicity
- Clear function separation:
  - `validate_startup()` - Check folders and file counts
  - `discover_files()` - Find and pair .txt files
  - `validate_url()` - Three-stage URL validation
  - `read_file()` - Read and strip content
  - `extract_image_filename()` - Get filename from URL
  - `generate_markdown()` - Create .md content
  - `create_failure_report()` - Generate FAILURE.md
  - `create_summary_report()` - Generate processing_summary.md
  - `main()` - Orchestrate processing flow

**Dependencies Management**

```txt
# requirements.txt
loguru==0.7.2
natsort==8.4.0
rich==13.7.0
alive-progress==3.1.5
requests==2.31.0
```

### 05.8 Performance Characteristics

**Sequential Processing**

- Process one file pair at a time
- No parallel processing
- Deterministic order (natsort)
- Memory efficient

**Expected Performance**

- Small datasets (10-50 pairs): ~5-15 seconds
- Medium datasets (50-200 pairs): ~30-90 seconds
- Large datasets (200+ pairs): ~2-5 minutes

**Performance Factors**

- URL validation (HTTP HEAD request) is slowest operation
- Network latency affects URL accessibility checks
- Disk I/O is minimal (small text files)
- Progress bar updates have negligible overhead

---

## 06. Success Criteria

### 06.1 Functional Requirements

**Must Have**
- ✅ Validate equal count of .txt files in LINKS and PROMPTS folders
- ✅ Pair files by natsort position
- ✅ Validate URL format, image extension, and accessibility
- ✅ Generate formatted Markdown files with embedded images
- ✅ Create timestamped output folder: `YYMMDD_HHMMSS_IMG-TO-IMG-MD`
- ✅ Fail fast on any error with detailed FAILURE.md
- ✅ Show comprehensive progress with alive-progress
- ✅ Log operations with Loguru and Rich
- ✅ Generate human-readable processing summary

**Should Have**
- ✅ Strip whitespace from URLs and prompts
- ✅ Ignore non-.txt files in input folders
- ✅ Extract image filename from URL for headers
- ✅ Display current processing phase in progress bar
- ✅ Color-coded console output (Rich)

**Won't Have**
- ❌ Configuration files
- ❌ Profile support
- ❌ Partial processing (continue on errors)
- ❌ Dry-run mode
- ❌ Recovery mechanisms
- ❌ Parallel processing

### 06.2 Code Quality Requirements

- ✅ Single file under 250 lines
- ✅ Type hints on all functions
- ✅ pathlib.Path for file operations
- ✅ Clear function names
- ✅ Docstrings on all functions
- ✅ No premature abstractions
- ✅ No custom frameworks

### 06.3 User Experience Requirements

- ✅ Zero-setup execution with `python3 run.py`
- ✅ Clear error messages with actionable solutions
- ✅ Comprehensive progress display
- ✅ Human-readable summary report
- ✅ Detailed technical logs for debugging

---

## 07. Implementation Phases

### Phase 1: Core Structure (Foundation)

**Deliverables**
- Project folder structure
- `requirements.txt` with dependencies
- `run.py` wrapper script
- Basic `src/main.py` skeleton

**Validation**
- `python3 run.py` creates venv and installs dependencies

### Phase 2: Input Discovery and Validation

**Deliverables**
- Folder existence validation
- .txt file discovery with natsort
- File count validation
- File pairing logic

**Validation**
- Script exits with clear error if folders missing
- Script exits with clear error if file counts don't match
- Script correctly pairs files by natsort position

### Phase 3: URL Validation

**Deliverables**
- URL format validation
- Image extension validation
- URL accessibility validation (HTTP HEAD)
- Image filename extraction

**Validation**
- Invalid URLs cause immediate failure
- Non-image URLs cause immediate failure
- Unreachable URLs cause immediate failure

### Phase 4: Markdown Generation

**Deliverables**
- Read LINKS and PROMPTS files
- Strip whitespace from content
- Generate formatted Markdown
- Write .md files to output folder

**Validation**
- Generated .md files match template structure
- Headers show extracted image filename
- TEXT SOURCE shows PROMPTS filename
- Whitespace stripped correctly

### Phase 5: Progress and Logging

**Deliverables**
- alive-progress integration
- Rich console output
- Loguru technical logging
- Markdown summary report generation

**Validation**
- Progress bar shows current file and phase
- Console output color-coded
- processing.log contains all operations
- processing_summary.md contains overview

### Phase 6: Error Handling

**Deliverables**
- FAILURE.md generation
- Detailed error messages
- Actionable solution steps
- Graceful script termination

**Validation**
- All error scenarios create FAILURE.md
- FAILURE.md contains file pair info
- FAILURE.md contains actionable solutions
- Script exits with code 1 on errors

### Phase 7: Testing and Refinement

**Deliverables**
- Manual testing with various scenarios
- Edge case handling verification
- Performance validation
- Documentation updates

**Validation**
- Script handles empty files
- Script handles invalid URLs
- Script handles unreachable URLs
- Script handles missing folders
- Script handles file count mismatches

---

## 08. Appendix

### 08.1 Example File Contents

**04.1.LINKS/link001.txt**
```
https://f003.backblazeb2.com/file/isof-bucket/batch6_upscaled/prompt09.0.png
```

**04.2_PROMPTS/prompt001.txt**
```
A man carries heavy bags on a ship dock.
```

**05.OUTPUT/250131_143022_IMG-TO-IMG-MD/link001.md**
```markdown
---

# prompt09.0.png

| IMAGE SOURCE: prompt09.0.png                                                           |
| -------------------------------------------------------------------------------------- |
| ![image](https://f003.backblazeb2.com/file/isof-bucket/batch6_upscaled/prompt09.0.png) |

**TEXT SOURCE: prompt001.txt:**

```text
A man carries heavy bags on a ship dock.
```

---
```

### 08.2 Command Reference

**Run the script**
```bash
python3 run.py
```

**Activate venv manually (optional)**
```bash
source venv/bin/activate  # macOS/Linux
python3 -m src.main
```

**Install dependencies manually (optional)**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 08.3 Troubleshooting Guide

**Error: Folders not found**
- Solution: Create `USER-FILES/04.INPUT/04.1.LINKS/` and `USER-FILES/04.INPUT/04.2_PROMPTS/`

**Error: File count mismatch**
- Solution: Ensure equal number of .txt files in both LINKS and PROMPTS folders

**Error: Invalid URL format**
- Solution: Check LINKS file contains valid HTTP/HTTPS URL

**Error: URL not accessible**
- Solution: Verify URL is reachable (check network connection, URL validity)

**Error: URL not an image**
- Solution: Ensure URL ends with image extension (.png, .jpg, .jpeg, .gif, .webp)

**Error: Empty file**
- Solution: Ensure all .txt files have content (URL or prompt text)

### 08.4 Future Enhancements (Not in Scope)

- Batch size limits
- Resume from failure
- Duplicate detection
- Custom markdown templates
- Image download and local embedding
- Multi-format output (HTML, PDF)
- Configuration file support
- Parallel processing option

---

**Document Version**: 1.0  
**Last Updated**: 2025-01-31  
**Status**: Final  
**Author**: Generated from idea brief and user responses
