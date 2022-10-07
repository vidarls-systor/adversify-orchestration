"""Orchestrates the process of extracting article text from a search result url

Target is to end up with the best possible context for classification.
"""

import logging
import GoogleMetadata
import azure.functions as func
import azure.durable_functions as df

def orchestrator_function(context: df.DurableOrchestrationContext):
    """"Orchestrates getting text representation from a search result
    
    Will do the following steps:
    1. Extract metadata from the search result. This will be used
       to create better context in case no further text can be extracted.
       It is also used to determine whether the URL is pointing to a resource
       that is unavailable for example due to paywall
    2. Download the content if NOT behind paywall
    3. Determine content type to determine what process to run for
       content extraction.
    3. For PDF, extract the content from PDF.
    4. For Html, extract the content from HTML.
    5. Puts together metadata and extracted text to form the snippet to classify

    Parameters
    ----------
    context: df.DurableOrchestrationContext
        Input must be the item dictionary from the 
        google search

    Returns
    -------

    """

    item_result = context.get_input()

    item_metadata = GoogleMetadata.get_metadata_for_item(item_result)
    if item_metadata['text_extraction_possible']:
        item_metadata = yield context.call_activity('DownloadAction', item_metadata)
    else:
        item_metadata['downloaded_content'] = None


    if item_metadata['downloaded_content']:
        if 'pdf' in item_metadata['downloaded_content']['content_type'].lower():
            item_metadata = yield context.call_activity('PdfTextExtractionAction', item_metadata)
        else:
            item_metadata = yield context.call_activity('HtmlTextExtractionAction', item_metadata)
    else:
        item_metadata['extracted_content'] = None         
    
    item_metadata = yield context.call_activity('CreateTextBodyAction', item_metadata)

    return item_metadata
    
main = df.Orchestrator.create(orchestrator_function)