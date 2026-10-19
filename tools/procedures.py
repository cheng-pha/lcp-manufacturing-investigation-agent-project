import os

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizableTextQuery


search_client = SearchClient(
    endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
    index_name=os.environ["AZURE_SEARCH_INDEX"],
    credential=AzureKeyCredential(
        os.environ["AZURE_SEARCH_KEY"]
    )
)


def search_procedures(query):
    vector_query = VectorizableTextQuery(
        text=query,
        k_nearest_neighbors=5,
        fields="text_vector"
    )

    results = search_client.search(
        search_text=query,
        vector_queries=[vector_query],
        select=["title", "chunk"],
        top=5
    )

    procedure_results = []

    for result in results:
        procedure_results.append(
            {
                "title": result["title"],
                "content": result["chunk"]
            }
        )

    return procedure_results