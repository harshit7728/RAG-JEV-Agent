
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.core.config import settings


def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    if not settings.gemini_api_key:
        raise ValueError("GEMINI_API_KEY is not configured")

    return GoogleGenerativeAIEmbeddings(
        model=settings.embedding_model,
        google_api_key=settings.gemini_api_key,
        output_dimensionality=settings.embedding_dimensions,
    )


async def embed_documents(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    embeddings = get_embeddings()
    return await embeddings.aembed_documents(texts)


async def embed_query(text: str) -> list[float]:
    embeddings = get_embeddings()
    return await embeddings.aembed_query(text)
