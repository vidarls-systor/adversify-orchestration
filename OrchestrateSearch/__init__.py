"""Main search orchestrator

Function responsible for orchestrating all
the sub processes involved in running an
adverse media search
"""
import Config
import logging
import json

import azure.functions as func
import azure.durable_functions as df


def orchestrator_function(context: df.DurableOrchestrationContext):
    """Orchestrator handling the outer orchestration of an adverse media lookup
    
    Executes the process of:

    1. Search (for each language)
        I.  For each result of each search: 
             a. Get metadata
             b. Attempt to get full article
        II. Get Aliases
    2. Using aliases across all languages:
        I. Run classification
    3. Sort results based on classification results

    Parameters
    ----------
    context: df.DurableOrchestrationContext
        Input is tuple with three elementes:
        (search_term, depth, selected_languages):
        * search_term: Name of person or organization to run adverse media lookup on
        * depth: how deep in search results to go (number of result pages to process)
        * selected_languages: which languages to process. (One search is done for each language)
          Not will only process languages that are available.
        
    Returns
    -------
    list[dict]
        Sorted results based on search engine ranking
        + classification results
    """

    languages = Config.get_configured_languages()
    if not languages:
        logging.error("No languages configured. Returning empty list")
        return []

    search_term, depth, selected_languages = context.get_input()
    # TODO: Log warning if any selected languages is not configured

    searches = [context.call_sub_orchestrator('OrchestrateLanguageSearch', (language, search_term, depth)) for language in selected_languages if language in languages]
    search_results = yield context.task_all(searches)
    search_results = [search_result for language_search_results in search_results for search_result in language_search_results]
    search_results.sort(key=lambda r: r['score'], reverse=True)
    return search_results

main = df.Orchestrator.create(orchestrator_function)