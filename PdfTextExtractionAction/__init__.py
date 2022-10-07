"""Activity function to extract text from downloaded PDF files"""

import Config
import logging

from azure.storage.blob.aio import BlobServiceClient
from io import BytesIO
from pdfminer.high_level import extract_text


async def main(itemMetadata: dict) -> dict:
    """Extracts text from the downloaded PDF file represented by the metadata
    
    Parameters
    ----------
    itemMetadata: dict
        Meta data for the search result item to extract text from
        needs to have the "downloaded_content" property set.

    Returns
    -------
    dict
        The Item metadata with teh property "extracted_content" set to
        a string of extracted content.
    """

    try:
        async with BlobServiceClient.from_connection_string(Config.get_function_local_blob_connection_string()) as blob_service_client:
            async with blob_service_client.get_blob_client(container = Config.get_blob_container_name(), blob = itemMetadata['downloaded_content']['blob_key']) as blob_client:
                # Do not do anything else if the blob already exists
                if await blob_client.exists():
                    blob_downloader = await blob_client.download_blob()
                    blob_content = BytesIO(await blob_downloader.readall())
                    extracted = extract_text(blob_content)
                    itemMetadata['extracted_content'] = extracted
                else:
                    itemMetadata['extracted_content'] = None

                return itemMetadata

    except Exception as e:
        logging.exception(f'Failed extracting content from {itemMetadata["id"]}', exc_info=e)
        itemMetadata['extracted_content'] = None
        return itemMetadata
