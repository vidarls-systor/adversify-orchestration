"""Activity function to collate gathered text into a body for classification"""

import logging


def main(itemMetadata: dict) -> dict:
    """Generates single string snippet for classification from the provided search result item
    
    Using extracted text and metadata, creates the best possible text body to submit for classification.

    Parameters
    ----------
    itemMetadata: dict
        Processed search result with extracted text and metadata

    Returns
    -------
    dict
        Item metadata with:
        1. Extracted content property removed (to avoid huge items due to large amounts of text)
        2. The property "text_body" set to the value that should be submitted to classification
           (if something fails, the text_body will be set to the content of "snippet")
    """

    try:
        text_body = ' ... '.join(itemMetadata['snippets'])
        if itemMetadata['extracted_content']:
            text_body = text_body + ' ... ' + itemMetadata['extracted_content']
        
        itemMetadata['extracted_content'] = None
        itemMetadata['text_body'] = text_body
        return itemMetadata
    except Exception as e:
        logging.exception(f'Error while creating text body for {itemMetadata["id"]}', exc_info=e)
        itemMetadata['extracted_content'] = None
        itemMetadata['text_body'] = itemMetadata['snippet']
        return itemMetadata
    
