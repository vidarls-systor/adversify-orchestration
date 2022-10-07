"""Activity function to execute classification of search result"""

import aiohttp
import Config
import logging

def to_classify_snippet(item:dict) -> dict:
    """Helper function to transform a processed search result into a classify request snippet object
    
    Parameters
    ----------
    item: dict
        Processed search result item to transform

    Returns
    -------
    dict
        Classify snippet dictionary.
    """

    return {
        'title': item['title'],
        'snippet': item['text_body'],
        'url': item['link'],
        'date': item['date']
    }

def to_scored_item(item:dict, score:dict) -> dict:
    """Helper function to apply scoring value to processed search result item
    
    Parameters
    ----------
    item: dict
        Processed search result item to transform
    score: dict
        The score of the search result item

    Returns
    -------
    dict
        Processed search result item with score applied
    """

    item['score'] = score['score']
    item['severity'] = score['severity']
    item['scoring_errors'] = score['error']
    item['scoring_title'] = score ['title']
    return item

def get_default_score(item:dict, error:str) -> dict: 
    """Helper function to generate a neutral scoring if something fails
    
    Parameters
    ----------
    item: dict
        Processed search result item to transform
    error: str
        Error text to apply to scoring metadata
    
    Returns
    -------
    dict
        Processed search result item with default score applied
    
    """
    return {
        'score': 0.0,
        'severity': 0.0,
        'error': error,
        'title': item['title']
    }

async def main(input: tuple[str,str,list[dict]]) -> list[dict]:
    """Submits a batch of prepared search results for classification
    
    Parameters
    ----------
    input: tuple[str,str,list[dict]]
        Input is a tuple of
        (language, search_term, results)

    Returns
    -------
    list[dict]
        input list of results augmented with
        classification results.
        Setting the properties:
        * `score`: The overall classification score
        * `severity`: Number indicating how much bad there is in the 
          source text
    """
    
    language, search_term, items = input
    try:
        request_data = {
            'name': search_term,
            'snippets': [to_classify_snippet(item) for item in items]
        }

        classify_url = Config.get_classify_url()

        async with aiohttp.ClientSession() as client:
            async with client.post(classify_url, json=request_data) as response:
                response.raise_for_status()
                response_data = await response.json()
                return [to_scored_item(item, score) for (item, score) in  zip(items, response_data['scores'])]

    except Exception as e:
        logging.exception('Error while classifying batch', exc_info=e)
        return [to_scored_item(item, get_default_score(item, 'Classification call failed')) for item in  items]