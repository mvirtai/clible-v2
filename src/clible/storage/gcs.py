"""Google Cloud Storage upload and download helpers.

Uses Application Default Credentials (ADC) or GOOGLE_APPLICATION_CREDENTIALS.
"""

from pathlib import Path

from google.cloud.storage import Client


def parse_gcs_uri(gcs_uri: str) -> tuple[str, str]:
    """Parse a GCS URI into bucket and object name.

    Args:
        gcs_uri: GCS URI in the format ``gs://bucket/path/to/object``.

    Returns:
        Tuple of ``(bucket_name, object_name)``.

    Raises:
        ValueError: If the URI is not a valid ``gs://`` path.
    """
    if not gcs_uri.startswith("gs://"):
        raise ValueError("GCS URI must start with gs://")

    bucket_and_object = gcs_uri.removeprefix("gs://")
    bucket_name, _, object_name = bucket_and_object.partition("/")
    if not bucket_name or not object_name:
        raise ValueError("GCS URI must include both bucket and object path")

    return bucket_name, object_name


def upload_file(
    bucket_name: str,
    object_name: str,
    local_path: Path,
    timeout: int = 300,
) -> str:
    """Upload a local file to a GCS bucket.

    Args:
        bucket_name: Name of the GCS bucket.
        object_name: Destination object name (path) inside the bucket.
        local_path: Path to the local file to upload.
        timeout: Request timeout in seconds (default 300). Increase for large files
            or slow networks.

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
    blob.upload_from_filename(str(local_path), timeout=timeout)
    return f"gs://{bucket_name}/{object_name}"


def download_file(gcs_uri: str, local_path: Path) -> Path:
    """Download a GCS object to a local file path.

    Args:
        gcs_uri: GCS URI in the format ``gs://bucket/path/to/object``.
        local_path: Destination path on local disk.

    Returns:
        The local destination path.
    """
    bucket_name, object_name = parse_gcs_uri(gcs_uri)
    local_path = Path(local_path)
    local_path.parent.mkdir(parents=True, exist_ok=True)

    client = Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(object_name)
    blob.download_to_filename(str(local_path))
    return local_path
