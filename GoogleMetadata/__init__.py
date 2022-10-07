"""Functions for working with the metadata part of the Google search results"""

from dateutil import parser
import logging
from urllib.parse import quote

def _get_metadata_dictionary(item:dict) -> dict:
    """Returns the dictionary of metadata from a Google result item if available
    
    Parameters
    ----------
    item: dict
        Google search result item

    Returns
    -------
    dict:
        Metadata dictionary if present,
        othwerwise an empty dictionary
    """

    try:
        if 'pagemap' in item and 'metatags' in item['pagemap'] and len(item['pagemap']['metatags']) > 0:
            return item['pagemap']['metatags'][0]

        return {}
    
    except Exception as e:
        logging.exception("Error while attempting to extract metadata from item", exc_info=e)
        return {}

def _get_titles(item : dict, metadata: dict) -> list[str]:
    """Attempts to get the best possible titles for an item
    
    Some times more accurate titles are provided in the metadata
    from google.
    
    This function attempts to find them all and create a collection of them.

    Parameters
    ----------
    item: dict
        Raw search result item from Google
    
    metadata: dict
        Extracted metadata from the raw result item

    Returns
    list[str]
        List of titles found in the metadata 
        in addition to the always present title
        from the raw item.
    """

    titles = []
    titles.append(item['title'])

    if metadata and type(metadata) is dict:
        if 'og:title' in metadata:
            titles.append(metadata['og:title'])
        
        if 'twitter:title' in metadata:
            titles.append(metadata['twitter:title'])

        if 'title' in metadata:
            titles.append(metadata['title'])

    return titles

def _get_snippets(item:dict, metadata:dict) -> list[str]:
    """Extracts any text that may be used as snippets
    
    Some times there are longer more cohesive text snippets in
    the Google metadata than the default snippet
    
    This functions attempts to get all of them as a list
    
    Parameters
    ----------
    item: dict
        Raw search result item from Google
    
    metadata: dict
        Extracted metadata from the raw result item

    Returns
    list[str]
        List of snippets / descriptions found in the metadata 
        in addition to the always present text snippet
        from the raw item.
    """

    snippets = []
    snippets.append(item['snippet'])

    if (metadata and type(metadata) is dict):
        if 'og:description' in metadata:
            snippets.append(metadata['og:description'])

        if 'twitter:description' in metadata:
            snippets.append(metadata['twitter:description'])
    
    return snippets

def _text_extraction_possible(item:dict, metadata:dict) -> bool:
    """Attemtps to determine if it is possible to extract text from the source of the search result
    
    Parameters
    ----------
    item: dict
        Raw search result item from Google
    
    metadata: dict
        Extracted metadata from the raw result item

    Returns
    -------
    bool
        `False` if the source is either believed to be behind a paywall
        or if metadata indicates the source is a video
    """

    # If no metadata is available
    # assume text extraction is possible
    if (not metadata) or (not (type(metadata) is dict)):
        return True

    if 'lp:paywall' in metadata and metadata['lp:paywall'] == 'hard':
        return False

    if 'cxenseparse:nvl-smp-access' in metadata and metadata['cxenseparse:nvl-smp-access'] == 'subscriber':
        return False

    if 'og:type' in metadata and 'video' in metadata['og:type'].lower():
        return False

    return True

def _get_image(item:dict) -> str:
    """Attempts to get a usable image thumbnail url from the search result item

    Parameters
    ----------
    item:dict
        Raw search result item from Google

    Returns
    -------
    str
        Url of an image that can be used in presentation to represent the
        search result.
        It no valid image can be found, the value is None
    """

    # Image data is always in the pagemap part
    if not 'pagemap' in item:
        return None

    if 'cse_thumbnail' in item['pagemap']:
        if len(item['pagemap']['cse_thumbnail']) > 0 and 'src' in item['pagemap']['cse_thumbnail'][0]:
            possible_image = item['pagemap']['cse_thumbnail'][0]['src']

            if possible_image.lower().startswith('http'):
                return possible_image

    if 'cse_image' in item['pagemap']:
        if len(item['pagemap']['cse_image']) > 0 and 'src' in item['pagemap']['cse_image'][0]:
            possible_image = item['pagemap']['cse_image'][0]['src']

            if possible_image.lower().startswith('http'):
                return possible_image
    
    return None

def _get_date(item:dict, metadata:dict) -> str:
    """Attempts to get a creation date for the article from Google metadata
    
    Parameters
    ----------
    item: dict
        Raw search result item from Google
    
    metadata: dict
        Extracted metadata from the raw result item

    Returns
    -------
    str
        The most likely date as an ISO formatted datestring
        If no date is found, None is returned
    """

    # No metadata no date
    if (not metadata or not (type(metadata) is dict)):
        None

    def _get_if_date(key):
        if key in metadata:
            possible_date = metadata[key]
            try:
                return parser.parse(possible_date)
            except Exception as e:
                return None

    date_keys = ['article:published_time', 'dc.date.issued', 'article:modified_time']
    possible_dates = [_get_if_date(possible_date) for possible_date in date_keys]
    found_dates = [found_date.isoformat() for found_date in possible_dates if found_date]
    if (len(found_dates) > 0):
        return found_dates[0]
    
    return None

def _make_id(item:dict) -> str:
    """Attempts to make a reproducible string that can be used as an identifier of this exact search result
    
    Used for example as cache key
    
    Parameters
    ----------
    item: dict
        Raw search result item from Google
        
    Returns
    -------
    str:
        Id string
    """

    return quote(item['link'].replace('http://', '').replace('https://', ''))


def get_metadata_for_item(item:dict) -> dict:
    """Builds an easy to work with dictionary of metada for a Google search result
    
    Parameters
    ----------
    item:dict
        Raw search result item from Google
    
    Returns
    -------
    dict:
        Dictionary in this format:
        {
            'title': 'Main title of the search result',
            'titles': ['All', 'Possible titles', 'after checking', 'metadata'],
            'snippet': 'Main plain text snippet from search result',
            'html_snippet': '<strong>Main</strong>html snippet from search result',
            'snippets': ['All', 'Possible snippets', 'After checking','metadata'],
            'link': 'http://www.source.com/of/the-search/result',
            'text_extraction_possible: True | False, # True if not determined to be a video or behind paywall,
            'date': YYYY-MM-DDTHH:mm:ss | None # Date of creation if determined,
            'id': 'string ident' # String identifier we can use for referring to this result itemn later.
        }
    """
    raw_metadata = _get_metadata_dictionary(item)

    return {
        'title': item['title'],
        'titles': _get_titles(item, raw_metadata),
        'snippet': item['snippet'],
        'html_snippet': item['htmlSnippet'],
        'snippets': _get_snippets(item, raw_metadata),
        'link': item['link'],
        'text_extraction_possible': _text_extraction_possible(item, raw_metadata),
        'image': _get_image(item),
        'date': _get_date(item, raw_metadata),
        'id': _make_id(item)
    }