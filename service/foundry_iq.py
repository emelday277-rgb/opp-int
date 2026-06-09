import os
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
)
from azure.core.credentials import AzureKeyCredential
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
SEARCH_API_KEY = os.getenv("AZURE_SEARCH_API_KEY")
SEARCH_INDEX = os.getenv("AZURE_SEARCH_INDEX", "oppint-index")

FOUNDRY_ENDPOINT = os.getenv("AZURE_FOUNDRY_ENDPOINT")
FOUNDRY_API_KEY = os.getenv("AZURE_FOUNDRY_API_KEY")
# FOUNDRY_DEPLOYMENT = os.getenv("AZURE_FOUNDRY_DEPLOYMENT", "gpt-4o-mini")

# Initialize clients
credential = AzureKeyCredential(SEARCH_API_KEY)

index_client = SearchIndexClient(
    endpoint=SEARCH_ENDPOINT,
    credential=credential
)

# openai_client = OpenAI(
#     base_url=f"{os.getenv('AZURE_FOUNDRY_ENDPOINT').rstrip('/')}/openai/v1/",
#     api_key=os.getenv("AZURE_FOUNDRY_API_KEY")
# )
openai_client = OpenAI(
    base_url=f"{FOUNDRY_ENDPOINT.rstrip('/')}/openai/v1/",
    api_key=FOUNDRY_API_KEY
)


def ensure_index_exists():
    """Create the search index if it doesn't exist."""
    try:
        index_client.get_index(SEARCH_INDEX)
        print(f"Index '{SEARCH_INDEX}' already exists.")
    except Exception:
        print(f"Creating index '{SEARCH_INDEX}'...")
        fields = [
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SearchableField(name="content", type=SearchFieldDataType.String),
            SimpleField(name="doc_type", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="session_id", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="chunk_index", type=SearchFieldDataType.Int32),
        ]
        index = SearchIndex(name=SEARCH_INDEX, fields=fields)
        index_client.create_index(index)
        print(f"Index '{SEARCH_INDEX}' created.")


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> list[str]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks


def index_document(text: str, doc_type: str, session_id: str):
    """
    Index a document into Foundry IQ (Azure AI Search).
    doc_type: 'opportunity' or 'organization'
    session_id: unique ID for this analysis session
    """
    ensure_index_exists()

    search_client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=SEARCH_INDEX,
        credential=credential
    )

    chunks = chunk_text(text)
    documents = []

    for i, chunk in enumerate(chunks):
        documents.append({
            "id": f"{session_id}-{doc_type}-{i}",
            "content": chunk,
            "doc_type": doc_type,
            "session_id": session_id,
            "chunk_index": i
        })

    search_client.upload_documents(documents)
    print(f"Indexed {len(documents)} chunks for {doc_type} (session: {session_id})")


def retrieve_context(query: str, session_id: str, doc_type: str = None, top: int = 5) -> str:
    """
    Retrieve relevant context from Foundry IQ for a given query.
    Optionally filter by doc_type: 'opportunity' or 'organization'
    """
    search_client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=SEARCH_INDEX,
        credential=credential
    )

    filter_expr = f"session_id eq '{session_id}'"
    if doc_type:
        filter_expr += f" and doc_type eq '{doc_type}'"

    results = search_client.search(
        search_text=query,
        filter=filter_expr,
        top=top
    )

    context_pieces = [result["content"] for result in results]
    return "\n\n---\n\n".join(context_pieces)


def cleanup_session(session_id: str):
    """Remove all indexed documents for a session after analysis."""
    search_client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=SEARCH_INDEX,
        credential=credential
    )

    results = search_client.search(
        search_text="*",
        filter=f"session_id eq '{session_id}'",
        select=["id"]
    )

    ids_to_delete = [{"id": r["id"]} for r in results]
    if ids_to_delete:
        search_client.delete_documents(ids_to_delete)
        print(f"Cleaned up {len(ids_to_delete)} documents for session {session_id}")