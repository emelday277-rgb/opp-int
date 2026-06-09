from fastapi import UploadFile, HTTPException

MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".txt"}
MIN_TEXT_LENGTH = 100
MAX_ORG_FILES = 5

def validate_multiple_files(files: list, field_name: str) -> list:
    """Validates a list of uploaded files."""
    if not files:
        raise HTTPException(status_code=400, detail=f"{field_name}: At least one file is required.")
    if len(files) > MAX_ORG_FILES:
        raise HTTPException(status_code=400, detail=f"{field_name}: Maximum {MAX_ORG_FILES} files allowed.")
    return [validate_file_upload(f, f"{field_name} [{f.filename}]") for f in files]


def validate_file_upload(file: UploadFile, field_name: str) -> bytes:
    """
    Validates an uploaded file for type, size, and readability.
    Returns the file contents as bytes.
    """

    # Check filename exists
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail=f"{field_name}: No filename provided."
        )

    # Check extension
    filename = file.filename.lower()
    extension = None
    for ext in ALLOWED_EXTENSIONS:
        if filename.endswith(ext):
            extension = ext
            break

    if not extension:
        raise HTTPException(
            status_code=400,
            detail=f"{field_name}: Unsupported file type '{filename}'. Please upload a PDF or TXT file."
        )

    # Read contents
    contents = file.file.read()

    # Check file is not empty
    if len(contents) == 0:
        raise HTTPException(
            status_code=400,
            detail=f"{field_name}: The file '{file.filename}' is empty."
        )

    # Check file size
    if len(contents) > MAX_FILE_SIZE_BYTES:
        size_mb = len(contents) / (1024 * 1024)
        raise HTTPException(
            status_code=400,
            detail=f"{field_name}: File size {size_mb:.1f}MB exceeds the {MAX_FILE_SIZE_MB}MB limit."
        )

    return contents


def validate_extracted_text(text: str, field_name: str):
    """
    Validates that extracted text has enough content to analyze.
    """
    if not text or not text.strip():
        raise HTTPException(
            status_code=400,
            detail=f"{field_name}: Could not extract any text from the uploaded file. "
                   f"If this is a scanned PDF, please use a text-based PDF instead."
        )

    if len(text.strip()) < MIN_TEXT_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"{field_name}: The document appears too short to analyze "
                   f"({len(text.strip())} characters). Please provide a more detailed document."
        )