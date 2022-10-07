from opencensus.extension.azure.functions import OpenCensusExtension
from opencensus.trace import config_integration
from opencensus.trace.logging_exporter import LoggingExporter
import logging
import os

# Set up instrumentation using OpenCensus
# (https://docs.microsoft.com/en-us/azure/azure-monitor/app/opencensus-python)
# This code HAVE TO EXECUTE ON EVERY FUNCTION
# => every function MUST have `from Config import config`
# This is becaause the call to `OpenCensusExtension.configure()` adds
# the `.tracer` property to the function call context
# Failing to run this line will cause any calls tracing 
# dependencies to fail.
config_integration.trace_integrations(['aiohttp'])
OpenCensusExtension.configure()
# Disable Application insights if not wanted
# (For example for local dev, unit tests and end-to-end-tests)
app_insights_disabled = os.getenv('AzureFunctionsJobHost__logging__applicationInsights__samplingSettings__isEnabled', 'true').lower() == 'false'
if app_insights_disabled:
    OpenCensusExtension._exporter = LoggingExporter()

def _get_connection_string_components(connection_string:str) -> dict:
    """Splits a storage account connection string into its constituent parts
    
    Parameters
    ----------
    connection_string:str
        Connection string to split

    Returns
    -------
    dict:
        Dictionary of each key / value represented by the connection string
    """

    return { 
        pair[:split_pos] : pair[split_pos+1:] 
        for (pair, split_pos) 
        in [(pair, pair.find('=')) for pair in connection_string.split(';')]
    }


def get_configured_languages() -> dict:
    """Gets configured languages with configuration
    
    Languages are configured in several environment variables:
    NOTE:  For settings with a `language` prefix the hyphen (`-`) in 
           the language code must be replaced with underscore (`_`)
           in the environment variable name and be ALL LOWER CASE. 
    
    NOTE:  If all required settings are not available for
           a language, it will NOT be listed as an option

    * languages:                  Semicolon separated list of iso 4 char language codes that are 
                                  currently supported. (nb-NO;sv-SE;da-DK)
    * [language]__search_engine_id: Google search engine id for the given language.
                                   
    Returns
    -------
    dict
        Dictionary of supported languages with settings as sub keys:
        {
            'nb-NO': {
                'search_engine_id': [some value]
                'search_string': "The Search string for the language"
            }
        }
    """

    # This can be configured to be a row in a table store or something else
    # that can potentially be loaded at runtime
    # but for now, we keep it in code
    norwegian_search_string = """Hvitvasking OR Heleri OR Tyveri OR Underslag OR Ran OR Utpressing OR Bedrageri OR Skattesvik OR Korrupsjon OR "Økonomisk utroskap" OR Terrorfinansiering OR Arbeidslivskriminalitet OR Konkurskriminalitet OR Miljøkriminalitet OR Regnskapskriminalitet OR Verdipapirkriminalitet OR Fakturasvindel OR Investeringsbedrageri OR Direktørbedrageri OR Olga-svindel OR Akvakulturkriminalitet OR "2Svart arbeid" OR "Økonomisk kriminalitet" OR Pengemuldyr OR Narkotika OR Smugling OR Kokain OR Heroin OR Skatteparadis OR Afghanistan OR Barbados OR Burkina OR Faso OR Caymanøyene OR Haiti OR Filippinene OR Iran OR Jamaica OR Jemen OR Jordan OR Kambodsja OR Mali OR Marokko OR Myanmar OR Nicaragua OR Nord-Korea OR Pakistan OR Panama OR Senegal OR Syria OR Sør-Sudan OR "Trinidad og Tobago" OR Uganda OR Vanuatu OR Zimbabwe OR Albania OR Forente OR Arabiske OR Emirater OR Malta OR Tyrkia OR Yemen OR Grønnvasking OR Faunakriminalitet OR Menneskesmugling OR Anmeldt OR Ulovlig OR Kriminell OR Lønnstyveri OR Hasj OR Marihuana OR Ekstremist OR Radikal OR Overgrep OR Forsikringssvindel OR Terrorist OR Militant OR Sedelighet OR Innsidehandel OR arrestert OR krypto OR kryptovaluta OR "virtuell valuta" OR bitcoin OR ethereum"""
    swedish_search_string = """Penningtvätt OR Häleri OR Stöld OR tjuveri OR Förskingring OR Rån OR Utpressning OR Bedrägeri OR Skattebrott OR Korruption OR terroristfinansiering OR konkursbrott OR Miljöbrott OR Bokföringsbrott OR Finansmarknadsbrott OR Fakturabedrägeri OR fordringsbedrägeri OR Investeringsbedrägeri OR VD-bedrägeri OR "Olga bedrägeri" OR Svartarbete OR "Ekonomisk brottslighet" OR ekobrott OR bulvan OR Narkotika OR Smuggling OR Kokain OR Heroin OR Skatteparadis OR Afghanistan OR Barbados OR "Burkina Faso" OR Caymanöarna OR Kajmanöarna OR Haiti OR Filippinerna OR Iran OR Jamaica OR Jemen OR Jordanien OR Kambodja OR Mali OR Marocko OR Myanmar OR Nicaragua OR Nordkorea OR Pakistan OR Panama OR Senegal OR Syrien OR Sydsudan OR "Trinidad och Tobago" OR Uganda OR Vanuatu OR Zimbabwe OR Albanien OR "Förenade arabemiraten" OR Malta OR Turkiet OR Jemen OR Greenwashing OR grönmålning OR gröntvättning OR Viltbrott OR Människosmuggling OR Anmäld OR Olagligt OR Kriminell OR Brottslig OR Lönestöld OR hasch OR marijuana OR Extremist OR Radikal OR övergrepp OR Försäkringsbedrägeri OR Terrorist OR Militant OR Sedlighet OR Insiderbrott OR arresterad OR krypto OR Kryptovaluta OR "digital valuta" OR bitcoin OR ethereum OR Cannabis OR Subventionsmissbruk OR Borgenärsbrott OR "Brott mot låneförbudet" OR  "Målvaktsbestämmelsen" OR "Skatteredovisningsbrott" OR "vårdslös skatteredovisning" OR "vårdslös skatteuppgift" OR "EU-bedrägeri" OR Marknadsmanipulation OR Marknadsmissbruk OR Omställningsstödsbrott OR "Organiserad brottslighet" OR Svindleri OR Bidragsbrott OR "Trolöshet mot huvudman" OR Urkundsförfalskning OR Kortbedräger"""
    danish_search_string = """Hvidvaskning OR Hæleri OR Tyveri OR Underslæb OR Røveri OR Afpresning OR Bedrageri OR skattesvig OR Skatteunddragelse OR Korruption OR terrorfinansiering OR Arbejdskriminalitet OR arbejdsmiljøforbrydelser OR Konkurskriminalitet OR Konkursrytteri OR Miljøkriminalitet OR regnskabsforbrydelser OR bogføringsforbrydelser OR Værdipapirbedrageri OR fakturasvig OR investeringssvig OR Direktørsvindel OR "Sort arbejde" OR "Økonomisk kriminalitet" OR pengemuldyr OR Narkotika OR Smugleri OR Kokain OR Heroin OR Skattely OR Afghanistan OR Barbados OR "Burkina Faso" OR Caymanøerne OR Haiti OR Filippinerne OR Iran OR Jamaica OR Yemen OR Jordan OR Cambodja OR Mali OR Marokko OR Myanmar OR Nicaragua OR Nordkorea OR Pakistan OR Panama OR Senegal OR Syrien OR Sydsudan OR "Trinidad og Tobago" OR Uganda OR Vanuatu OR Zimbabwe OR Albanien OR "Forenede Arabiske Emirater" OR Malta OR Tyrkiet OR Grønvask OR grønvaskning OR faunakriminalitet OR Menneskesmugling OR Anmeldt OR Ulovligt OR Kriminel OR Løntyveri OR hamp OR marihuana OR Ekstremist OR Radikal OR Overfald OR Forsikringssvig OR Forsikringssvindel OR Terrorist OR Militant OR Sedelighet OR insiderhandel OR anholdt OR krypto OR kryptovaluta OR "virtuell valuta" OR bitcoin OR ethereum OR Skyldnersvig OR Afgiftsunddragelse OR Toldkriminalitet OR Valutakriminalitet OR Momssvig OR Kursmanipulation OR "leasing-karrusel" """

    language_search_strings = {
        'nb_no': norwegian_search_string,
        'sv_se': swedish_search_string,
        'da_dk': danish_search_string
    }

    supported_languages = {}

    defined_languages_settings_string = os.getenv('languages') if os.getenv('languages') else ''
    defined_languages_strings = defined_languages_settings_string.split(';')

    for language in defined_languages_strings:
        logging.info(language)
        # Collect all settings of language
        language_slug = language.lower().replace("-","_")
        language_search_engine_key = f'{language_slug}__search_engine_id'
        language_search_engine = os.getenv(language_search_engine_key)
        # Check that all settings are present
        if language_search_engine and language_slug in language_search_strings:
            supported_languages[language] = {
                'search_engine_id': language_search_engine,
                'search_string': language_search_strings[language_slug]
            }
    
    return supported_languages

def get_google_api_key() -> str:
    """Gets the configured Google API key for the application
    
    Stored in the environment variable named `google_api_key`
    """

    return os.getenv('google_api_key')

def get_function_local_blob_connection_string() -> str:
    """Returns the configured function local connection string for blob storage
    
    Reads the connection string configured in the `AzureWebJobsStorage` environment
    variable.

    Includes special logic to handle the following cases:

    1. The special `UseDevelopmentStorage=True` connection string is used.
       Returns hard-coded connection string with local emulator endpoint
       for blob storage configured.
    2. Generic connection string for a storage account without the blob storage 
       endpoint specified.
    3. Connection string with explicitly configured blob storage endpoint.

    Returns
    -------
    str:
        Storage account connection string with explicitly configured blob storage endpoint.
    """

    connection_string = os.environ['AzureWebJobsStorage']
    # Special case for local development
    if connection_string == 'UseDevelopmentStorage=true':
        return 'AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;DefaultEndpointsProtocol=http;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1'
    # Table endpoint already in connection string
    if "BlobEndpoint" in connection_string:
        return connection_string

    components = _get_connection_string_components(connection_string)
    blob_endpoint = f"{components['DefaultEndpointsProtocol']}://{components['AccountName']}.blob.{components['EndpointSuffix']}/"
    return f'{connection_string};BlobEndpoint={blob_endpoint}'

def get_blob_container_name() -> str:
    """Gets the name of the blob container to be used for saving downloads
    
    Stored in the environment variable named `DownloadsContainerName`
    """

    return os.getenv('DownloadsContainerName')

def get_classify_batch_size() -> int:
    """Gets the configured max batch size for calls to the classifier in KB
    
    Stored in the environment variable named `classify_batch_size`

    Returns
    -------
    int:
        Max match size in KB for calls to classify. 
        Defaults to 300 if not set
    """

    return int(os.getenv('classify_batch_size', '300'))

def get_classify_url() -> str:
    """Gets the url for the classification service
    
    Stored in the environment variable named `classify_url`

    Returns
    -------
    str
        Url of classification service
    """

    return os.getenv('classify_url')
