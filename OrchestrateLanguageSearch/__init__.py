"""Orchestrates the flow of a single language search

Called once for each language from the main orchestrator
"""

import logging
import json

import azure.functions as func
import azure.durable_functions as df


def orchestrator_function(context: df.DurableOrchestrationContext):
    """Orchestrates an adverse media search for one language.
    
    1. Execute google search
    2. Extract text from results
    3. Extract aliases

    Parameters
    ----------
    context: df.DurableOrchestrationContext
        Input must be tuple of (language, search_term, depth)
    """

    language, search_term, depth = context.get_input()

    search_results = yield context.call_activity('SearchAction', (language, search_term, depth))
    processing_tasks = [context.call_sub_orchestrator('OrchestrateTextExtraction', search_result) for search_result in search_results]
    processing_results = yield context.task_all(processing_tasks)
    
    batches = yield context.call_activity('ClassifyBatchingAction', processing_results)

    scoring_tasks = [context.call_activity('ClassifyAction', (language, search_term, batch)) for batch in batches]
    scoring_results = yield context.task_all(scoring_tasks)
   
    return [scoring_result for scoring_result_batch in scoring_results for scoring_result in scoring_result_batch]

main = df.Orchestrator.create(orchestrator_function)