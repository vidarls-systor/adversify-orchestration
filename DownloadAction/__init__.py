"""Action function that downloads the content of a url and saves it to blob storage

If the website has been downloaded before (within reasonable time), the data is not re-downloaded.
"""

import aiohttp
import Config
import logging

from azure.storage.blob import BlobType, ContentSettings
from azure.storage.blob.aio import BlobServiceClient

async def main(itemMetadata: dict) -> str:
    """Action function that downloads the content of a url and saves it to blob storage
    
    If the content has been downloaded before, the blob key of the previously downloaded data is returned.

    If the content can not be downloaded, the string "NOCONTENT" is returned.

    Parameters
    ----------
    itemMetadata: dict
        Item metadata of the search result to download.
        (As created by )
    Returns
    -------
    dict
        Item metadata with the property 'downloaded_content' set to a dictionary with this structure:
        {
            'blob_key': key of the created blob,
            'content_type': content type as returned by the server.
        }
        If no content was downloaded, the property is set to None.
    """

    try:
        async with BlobServiceClient.from_connection_string(Config.get_function_local_blob_connection_string()) as blob_service_client:
            async with blob_service_client.get_blob_client(container = Config.get_blob_container_name(), blob = itemMetadata['id']) as blob_client:
                # Do not do anything else if the blob already exists
                if await blob_client.exists():
                    blob_properties = await blob_client.get_blob_properties()

                    blob_metadata = {
                        'blob_key': itemMetadata['id'],
                        'content_type': blob_properties.content_settings.content_type
                    }

                    itemMetadata['downloaded_content'] = blob_metadata
                    return itemMetadata
                
                async with aiohttp.ClientSession() as client:
                    async with client.get(itemMetadata['link']) as response:
                        response.raise_for_status()
                        await blob_client.upload_blob(
                            data=await response.read(),
                            blob_type=BlobType.BLOCKBLOB,
                            length=response.content_length,
                            overwrite=True,
                            content_settings=ContentSettings(
                                content_type=response.content_type
                            )
                        )

                        blob_metadata = {
                            'blob_key': itemMetadata['id'],
                            'content_type': response.content_type
                        }

                        itemMetadata['downloaded_content'] = blob_metadata
                        return itemMetadata

    except Exception as e:
        logging.exception(f'Failed to download content from {itemMetadata["link"]}', exc_info=e)
        itemMetadata['downloaded_content'] = None
        return itemMetadata
