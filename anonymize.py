import argparse
import logging
import os
import shutil
import subprocess
import zipfile

import gradio as gr


# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description="Anonymize DICOM zip file")
parser.add_argument(
    "--anonymizer",
    type=str,
    default="/root/DICOMAnonymizer/anonymize",
    help="Path to the anonymizer executable"
)
args = parser.parse_args()


def handle_file(file):
    if not file:
        logger.warning("No file uploaded")
        return

    logger.info(f"File received: {file.name}")

    unzipped_dir = os.path.splitext(file.name)[0]
    anonymized_dir = os.path.splitext(file.name)[0] + "_anonymized"
    anonymized_filename = os.path.splitext(file.name)[0] + "_anonymized.zip"

    # Unzip the uploaded file
    gr.Info(f"Unzipping : {os.path.basename(file.name)}")
    with zipfile.ZipFile(file.name, "r") as zip_ref:
        zip_ref.extractall(unzipped_dir)
    logger.info(f"File unzipped at: {unzipped_dir}")

    # Run the anonymizer executable
    gr.Info(f"Anonymizing : {os.path.basename(file.name)}")
    subprocess.run(
        [
            args.anonymizer,
            "-i", unzipped_dir,
            "-o", anonymized_dir,
            "-b",
            "-p", "hashuid"
        ]
    )
    logger.info(f"Anonymized file created at: {anonymized_dir}")

    # Zip the anonymized file
    gr.Info(f"Zipping : {os.path.basename(anonymized_filename)}")
    shutil.make_archive(anonymized_dir, "zip", anonymized_dir)
    logger.info(f"Anonymized file zipped at: {anonymized_filename}")

    # remove the unzipped and anonymized directories
    shutil.rmtree(unzipped_dir)
    shutil.rmtree(anonymized_dir)
    logger.info(f"Cleaned up files for: {unzipped_dir}, {anonymized_dir}")

    return anonymized_dir + ".zip"


# Launch the Gradio interface
with gr.Blocks(title="Anonymize DICOM zip file",
               delete_cache=(86400, 86400)) as demo:
    gr.Markdown("# Anonymize a DICOM zip file")
    file_input = gr.File(
        label="Upload your DICOM zip file", file_types=[".zip"],
        interactive=True
    )
    file_output = gr.File(
        label="Download anonymized DICOM zip file",
        interactive=False
    )
    file_input.change(handle_file, inputs=file_input, outputs=file_output)

demo.launch()
