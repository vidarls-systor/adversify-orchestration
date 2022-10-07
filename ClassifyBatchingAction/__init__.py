"""Activity function that divides the input data into batches

Uses the byte-ish size of the snippets to guide the batch size
"""

import Config
import logging


def main(items: list[dict]) -> list[list[dict]]:
    """Divides the incoming list of processed search result items into batches
    
    To efficiently call the classifier, we ned to create sensible batches sizes
    to balance number of calls with the text size required to be processed.

    The byte size of the combined text bodies of a batch is what determines
    the number of batches.

    Once the size of a batch reaches the configured max batch size
    a new batch is created.

    Parameters
    ----------
    items: list[dict]
        Search result items processed to create the best possible text bodies for searching.

    Returns
    -------
    list[list[dict]]
        The incoming items divided into roughly equally sized 
        batches. (Equally sized on data length, no number of items)
    """
    try:
        current_batch_length = 0
        current_batch = []
        batches = []
        max_batch_size = Config.get_classify_batch_size() * 1000

        for item in items:
            current_batch.append(item)
            current_batch_length = current_batch_length + len(item['text_body'].encode('utf-8'))
            if (current_batch_length > max_batch_size):
                batches.append(current_batch)
                current_batch = []

        # add the last unfinished batch if it has any items
        if len(current_batch) > 0:
            batches.append(current_batch)

        return batches
    except Exception as e:
        logging.exception('Failed batching results for classification', exc_info=e)
        return [items]
