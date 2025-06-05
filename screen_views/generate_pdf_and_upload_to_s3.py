import subprocess
import tempfile
import os
import sys  # <-- ADD THIS
from pathlib import Path
from django.conf import settings
import boto3
from botocore.exceptions import BotoCoreError, ClientError
import logging

logger = logging.getLogger(__name__)

def generate_pdf_and_upload_to_s3(url: str, token: str) -> str:
    """
    Generates a PDF from a URL using pyppeteer (in a subprocess), uploads it to S3, and returns the S3 URL.
    Raises ValueError if url or token is missing.
    """
    if not url or not token:
        logger.error(f"URL or token is None. url={url!r}, token={token!r}")
        raise ValueError("Both url and token must be provided and not None.")

    # The Python script to run as a subprocess
    worker_script = '''
import asyncio
import sys
import uuid
from pathlib import Path
from pyppeteer import launch

async def generate_pdf(url: str, token: str) -> str:
    browser = await launch(
        headless=True,
        args=['--no-sandbox'],
        executablePath="C:\\\\Program Files\\\\Google\\\\Chrome\\\\Application\\\\chrome.exe"
    )
    page = await browser.newPage()
    full_url = f"{url}?token={token}"
    await page.goto(full_url, {"waitUntil": "networkidle0"})

    pdf_dir = Path('.') / 'public'
    pdf_dir.mkdir(exist_ok=True)
    file_name = f"report_{uuid.uuid4().hex[:8]}.pdf"
    file_path = pdf_dir / file_name

    await page.pdf({
        'path': str(file_path),
        'format': 'A4',
        'printBackground': True,
        'margin': {'top': '1cm', 'bottom': '1cm', 'left': '1cm', 'right': '1cm'},
        'displayHeaderFooter': True,
        'footerTemplate': """
            <div style='width:100%; font-size:10px; padding:0 1cm; font-family:Arial; color:#888; display:flex; justify-content:space-between;'>
                <span>http://app.aams.io</span>
                <span>Page <span class='pageNumber'></span> of <span class='totalPages'></span></span>
            </div>
        """,
        'headerTemplate': '<div></div>',
        'scale': 0.9,
    })

    await browser.close()
    return str(file_path)

def main():
    url = sys.argv[1]
    token = sys.argv[2]
    try:
        pdf_path = asyncio.run(generate_pdf(url, token))
        print(pdf_path)  # output path
    except Exception as e:
        print(f"ERROR:{{e}}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
'''

    # Create a temporary .py file for the subprocess script
    with tempfile.NamedTemporaryFile('w', suffix='.py', delete=False) as tf:
        script_path = tf.name
        tf.write(worker_script)

    pdf_path = None
    try:
        # Use the same Python interpreter as the one running Django
        python_executable = sys.executable
        result = subprocess.run(
            [python_executable, script_path, url, token],
            capture_output=True,
            text=True,
            cwd=settings.BASE_DIR  # so 'public' folder resolves correctly
        )
        logger.info(f"Subprocess stdout: {result.stdout}")
        logger.error(f"Subprocess stderr: {result.stderr}")

        # Check for errors in subprocess
        if result.returncode != 0:
            logger.error(f"PDF generation subprocess failed: {result.stderr}")
            raise RuntimeError("Failed to generate PDF: " + result.stderr.strip())

        pdf_path = result.stdout.strip()
        if not pdf_path or not os.path.exists(pdf_path):
            logger.error("PDF was not generated or path is invalid.")
            raise RuntimeError("PDF generation failed: No output path returned.")

        # Upload PDF to S3
        s3_url = _upload_to_s3(pdf_path)

        # Clean up PDF file
        try:
            os.remove(pdf_path)
        except Exception as e:
            logger.warning(f"Failed to remove local PDF: {e}")

        return s3_url

    except Exception as e:
        logger.error(f"Error in PDF generation/upload: {e}", exc_info=True)
        raise

    finally:
        # Remove the temp script file
        if os.path.exists(script_path):
            os.remove(script_path)

def _upload_to_s3(file_path: str) -> str:
    """
    Uploads a file to S3 and returns the public URL.
    """
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=getattr(settings, 'AWS_REGION', None)
        )

        file_name = os.path.basename(file_path)
        s3.upload_file(
            Filename=file_path,
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=file_name,
            ExtraArgs={'ACL': 'public-read'}
        )

        s3_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{file_name}"
        logger.info(f"Successfully uploaded PDF to S3: {s3_url}")
        return s3_url

    except (BotoCoreError, ClientError) as e:
        logger.error(f"Failed to upload file to S3: {e}", exc_info=True)
        raise
