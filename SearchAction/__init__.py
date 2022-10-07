"""Executes a search towards google custom search engine"""

import aiohttp
import Config
import logging

google_custom_search_url = 'https://www.googleapis.com/customsearch/v1'

async def main(input: tuple[str,str,int]) -> str:
    """Search for given name in AML context within a provided language
    
    Uses Google custom search engine (https://developers.google.com/custom-search/)
    to search the internet for the provided name. Within the context of AML and country 
    / language.

    The provided country / language parameter decideds which keywords to use and which 
    programmable search engine to use.

    Unsupported languages will simply return an empty list.

    Parameters
    ----------
    input: tuple[str,str, depth]
        Tuple with the first element being the iso language code
        and the second being the name to search for, and the second the
        number of pages to process.
        `("nb-NO", "My name", 3)`
    
    Returns
    -------
    list[dict]
        List of results
    """

    language, search_term, depth = input


    languages = Config.get_configured_languages()
    google_api_key = Config.get_google_api_key()
    language_settings = languages[language]

    search_string = f'"{search_term}" AND ({language_settings["search_string"]})'
    page = 1
    nextIndex = 1
    has_more_pages = True
    all_results = []

    async with aiohttp.ClientSession() as client:
        while has_more_pages and page <= depth:
            page = page + 1
            async with client.get(f'{google_custom_search_url}?cx={language_settings["search_engine_id"]}&start={nextIndex}&key={google_api_key}&q={search_string}') as response:
                try:
                    response.raise_for_status()
                    response_content = await response.json()
                    all_results.append(response_content)

                    # Check if more pages are available
                    if 'queries' in response_content and 'nextPage' in response_content['queries']:
                        has_more_pages = True
                        nextIndex = response_content['queries']['nextPage'][0]['startIndex']
                    else:
                        has_more_pages = False
                except Exception as e:
                    logging.exception(f'Failed to get google search results for {search_term}', exc_info=e)
                    logging.error(f'Response status: {response.status}')
                    content_as_text = await response.text()
                    logging.error(f'Respone content: {content_as_text}')
                    raise

    return [item for result in all_results for item in result['items']]
