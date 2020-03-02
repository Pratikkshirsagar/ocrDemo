import ocrmypdf
from google.cloud import storage
from PyPDF2 import PdfFileWriter, PdfFileReader
from google.cloud import vision_v1
from google.cloud.vision_v1 import enums
import six
import os

import firebase_admin
from firebase_admin import auth
from firebase_admin import credentials
from google.cloud import firestore
import numpy as np
from elasticsearch import Elasticsearch

es = Elasticsearch(HOST="http://localhost:", PORT=9200)
es = Elasticsearch()


# function for randome id genertion
def randome_id():
    ran_num = np.random.choice(range(2000), 1, replace=False)
    return ran_num[0]


# function to save in elastic
def save_to_elasticsearch(main_pdf_path, split_pad_page_path, ocr_text_data):
    elk_key = f"{main_pdf_path}***{split_pad_page_path}"
    print(elk_key)
    doc = {elk_key: ocr_text_data}
    index_id = randome_id()
    result = es.index(index="pratik_pdfs", id=index_id, body=doc)
    print(result)


# function  to ocr the split pdf
def sample_batch_annotate_files(storage_uri, gcp_main_pdf_file_path):

    client = vision_v1.ImageAnnotatorClient()

    if isinstance(storage_uri, six.binary_type):
        storage_uri = storage_uri.decode("utf-8")

    gcs_source = {"uri": storage_uri}
    mime_type = "application/pdf"
    input_config = {"gcs_source": gcs_source, "mime_type": mime_type}
    type_ = enums.Feature.Type.DOCUMENT_TEXT_DETECTION
    features_element = {"type": type_}
    features = [features_element]

    pages_element = 1
    pages = [pages_element]
    requests_element = {
        "input_config": input_config,
        "features": features,
        "pages": pages,
    }
    requests = [requests_element]

    response = client.batch_annotate_files(requests)
    for image_response in response.responses[0].responses:
        text_data = image_response.full_text_annotation.text
        save_to_elasticsearch(gcp_main_pdf_file_path, storage_uri, text_data)


def delete_local_file(path):
    if os.path.exists(path):
        os.remove(path)
    else:
        print("File does not exist")


# MAIN FUNCTION
def get_the_pdf_from_firestore(bucket_name, source_blob_name, destination_file_name):

    # get the pdf from firestore
    storage_client = storage.Client()
    des_file_name = f"{destination_file_name}/{source_blob_name}"
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(des_file_name)

    # convert it into searchable pdf
    myocrpdfpath = f"/Users/pratik/Desktop/test_ocr/outputpdf/{source_blob_name}"
    if __name__ == "__main__":
        try:
            # convert it to searchable pdf
            ocrmypdf.ocr(des_file_name, myocrpdfpath)
            full_pdf_path = (
                f"/Users/pratik/Desktop/test_ocr/outputpdf/{source_blob_name}"
            )
            bucket_name = "pratik_pdf_bucket"
            source_file_name = full_pdf_path
            # save to firestore
            bucket = storage_client.bucket(bucket_name)
            destination_blob_name_full_pdf = f"fullPDF/{source_blob_name}"
            blob = bucket.blob(destination_blob_name_full_pdf)
            blob.upload_from_filename(source_file_name)

            # split the searchable pdf
            inputpdf = PdfFileReader(open(myocrpdfpath, "rb"))
            for i in range(inputpdf.numPages):
                output = PdfFileWriter()
                output.addPage(inputpdf.getPage(i))
                fullpath = f"/Users/pratik/Desktop/test_ocr/pagepdf/{i}.pdf"
                outputFiles = open(fullpath, "wb")
                output.write(outputFiles)
                outputFiles.close()

                # saving it to firestore
                source_file_name = fullpath
                destination_blob_name_split_pdf = f"splitPDF/{source_blob_name}{i}.pdf"
                bucket = storage_client.bucket(bucket_name)
                blob = bucket.blob(destination_blob_name_split_pdf)
                blob.upload_from_filename(source_file_name)

                # ocr
                gcp_path_split_path = "gs://{}/{}".format(
                    bucket_name, destination_blob_name_split_pdf
                )
                gcp_full_pdf_path = "gs://{}/{}".format(
                    bucket_name, destination_blob_name_full_pdf
                )
                sample_batch_annotate_files(gcp_path_split_path, gcp_full_pdf_path)

                # DELETE THE FILE FROM LOCAL STORAGE
                delete_local_file(fullpath)

            # DELETE FROM LOCAL STORAGE
            delete_local_file(full_pdf_path)
            delete_local_file(des_file_name)
        except:
            full_pdf_path = f"/Users/pratik/Desktop/test_ocr/pdf/{source_blob_name}"
            bucket_name = "pratik_pdf_bucket"
            source_file_name = full_pdf_path
            # save to firestore
            bucket = storage_client.bucket(bucket_name)
            destination_blob_name_full_pdf = f"fullPDF/{source_blob_name}"
            blob = bucket.blob(destination_blob_name_full_pdf)
            blob.upload_from_filename(source_file_name)

            inputpdf = PdfFileReader(open(des_file_name, "rb"))
            for i in range(inputpdf.numPages):
                output = PdfFileWriter()
                output.addPage(inputpdf.getPage(i))
                fullpath = f"/Users/pratik/Desktop/test_ocr/pagepdf/{i}.pdf"
                outputFiles = open(fullpath, "wb")
                output.write(outputFiles)
                outputFiles.close()

                # saving it to firestore
                source_file_name = fullpath
                destination_blob_name_split_pdf = (
                    f"splitPDF/{source_blob_name}{i}.pdf"  # same goes hea
                )
                bucket = storage_client.bucket(bucket_name)
                blob = bucket.blob(destination_blob_name_split_pdf)
                blob.upload_from_filename(source_file_name)

                # ocr
                searchable_pdf_full_path = "gs://{}/{}".format(
                    bucket_name, source_blob_name
                )
                gcp_split_pdf_path = "gs://{}/{}".format(
                    bucket_name, destination_blob_name_split_pdf
                )
                gcp_full_pdf_path = "gs://{}/{}".format(
                    bucket_name, searchable_pdf_full_path
                )
                sample_batch_annotate_files(gcp_split_pdf_path, gcp_full_pdf_path)

                # DELETE THE FILE FROM LOCAL STORAGE
                delete_local_file(fullpath)

            # DELETE FROM LOCAL STORAGE
            delete_local_file(full_pdf_path)
            delete_local_file(des_file_name)


get_the_pdf_from_firestore(
    "test-ocr-259809.appspot.com", "A1bc.pdf", "/Users/pratik/Desktop/test_ocr/pdf"
)
