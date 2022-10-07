"""Main entry point for Adversify"""
 
import logging

import Config
import azure.functions as func
import azure.durable_functions as df


async def main(req: func.HttpRequest, starter: str) -> func.HttpResponse:
    """Main entry point for Adversify
    
    Starts the process of running an adverse media search for the given name.

    Parameters are expected as url parameters

    Parameters
    ----------
    req: func.HttpRequest
        Incoming http request that starts the lookup.
        Required a url parameter named:
        `name`: Name of the person to run adverse media search on

    starter: str
        Internal parameter, not used

    Returns
    -------
    HttpResponse
        Durable functions response with
        link to check status
    """

    # Validate configuration
    languages = Config.get_configured_languages()
    if not languages:
        return func.HttpResponse(
            status_code=500,
            body='No languages configured',
            mimetype='text/plain',
            charset='utf-8'
        )

    # Validate input
    name = req.params.get('name')
    if not name:
        return func.HttpResponse(
            status_code=400,
            body='Url parameter `name` required',
            mimetype='text/plain',
            charset='utf-8'
        )

    # Start process
    client = df.DurableOrchestrationClient(starter)
    instance_id = await client.start_new('OrchestrateSearch', None, (name, 3, [language for language in languages]))

    logging.info(f"Started orchestration with ID = '{instance_id}'.")

    return client.create_check_status_response(req, instance_id)