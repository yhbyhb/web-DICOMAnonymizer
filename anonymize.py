import gradio as gr
import shutil
import os
import subprocess
import zipfile
import logging

anonymizer = "/root/DICOMAnonymizer/anonymize"
option = "-b -p hashuid"

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def handle_file(file):
    if not file:
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
        [anonymizer, "-i", unzipped_dir, "-o", anonymized_dir, option]
    )
    logger.info(f"Anonymized file created at: {anonymized_dir}")

    # Zip the anonymized file
    gr.Info(f"Zipping result: {os.path.basename(anonymized_filename)}")
    shutil.make_archive(anonymized_dir, "zip", anonymized_dir)
    logger.info(f"Anonymized file zipped at: {anonymized_filename}")

    # remove the unzipped and anonymized directories
    shutil.rmtree(unzipped_dir)
    shutil.rmtree(anonymized_dir)
    logger.info(f"Cleaned up files for: {unzipped_dir}, {anonymized_dir}")

    return anonymized_dir + ".zip"


with gr.Blocks() as demo:
    gr.Markdown("# Anonymize zipped DICOM File")
    file_input = gr.File(
        label="Upload your zipped DICOM file", file_types=[".zip"],
        interactive=True
    )
    file_output = gr.File(
        label="Download anonymized zipped DICOM file",
        interactive=False
    )
    file_input.change(handle_file, inputs=file_input, outputs=file_output)

demo.launch(server_name="0.0.0.0")
