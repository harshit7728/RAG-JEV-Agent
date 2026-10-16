
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services.embeddings import embed_documents
from app.services.ingestion import extract_text, split_text

router = APIRouter(prefix="/documents", tags=["Documents"])

MAX_FILE_SIZE = 10 * 1024 * 1024


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    filename = file.filename or ""

    if filename.lower().rsplit(".", 1)[-1] not in {
        "pdf",
        "docx",
    }:
        raise HTTPException(
            status_code=415,
            detail="Only PDF and DOCX files are supported.",
        )

    file_bytes = await file.read(MAX_FILE_SIZE + 1)

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Maximum upload size is 10 MB.",
        )

    if not file_bytes:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty.",
        )

    try:
        text = extract_text(filename, file_bytes)
        chunks = split_text(text)

        if not chunks:
            raise ValueError("No text chunks were generated.")

        vectors = await embed_documents(chunks)

        if len(vectors) != len(chunks):
            raise RuntimeError(
                "Embedding count does not match chunk count."
            )

        if any(len(vector) != 768 for vector in vectors):
            raise RuntimeError(
                "Embedding dimension must be 768."
            )

        document = Document(
            title=filename,
            content=text,
            status="embedded",
        )
        db.add(document)
        await db.flush()

        db.add_all(
            [
                DocumentChunk(
                    document_id=document.id,
                    chunk_index=index,
                    content=chunk,
                    embedding=vector,
                )
                for index, (chunk, vector)
                in enumerate(zip(chunks, vectors))
            ]
        )

        await db.commit()

        return {
            "document_id": str(document.id),
            "filename": filename,
            "status": "embedded",
            "chunk_count": len(chunks),
        }

    except ValueError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        await db.rollback()
        # Log the exception internally in production.
        raise HTTPException(
            status_code=502,
            detail="Document processing failed.",
        ) from exc
