"""Google Cloud Storage upload for backup and related operations.

Uses Application Default Credentials (ADC) or GOOGLE_APPLICATION_CREDENTIALS.
"""

from pathlib import Path

from google.cloud.storage import Client


def upload_file(
    bucket_name: str,
    object_name: str,
    local_path: Path,
) -> str:
    """Upload a local file to a GCS bucket.

    Args:
        bucket_name: Name of the GCS bucket.
        object_name: Destination object name (path) inside the bucket.
        local_path: Path to the local file to upload.

    Returns:
        The gs:// URI of the uploaded object (gs://bucket/object_name).

    Raises:
        FileNotFoundError: If local_path does not exist.
        google.cloud.exceptions.NotFound: If the bucket does not exist.
    """
    local_path = Path(local_path)
    if not local_path.is_file():
        raise FileNotFoundError(f"Local file not found: {local_path}")

    client = Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(object_name)
    blob.upload_from_filename(str(local_path))
    return f"gs://{bucket_name}/{object_name}"
