
from io import BytesIO

import fitz
from docx import Document as DocxDocument
from langchain_text_splitters import RecursiveCharacterTextSplitter


def extract_text(
    filename: str,
    file_bytes: bytes,
) -> str:
    extension = filename.lower().rsplit(".", 1)[-1]

    if extension == "pdf":
        with fitz.open(
            stream=file_bytes,
            filetype="pdf",
        ) as pdf:
            pages = [
                page.get_text("text")
                for page in pdf
            ]
        text = "\n".join(pages)

    elif extension == "docx":
        document = DocxDocument(BytesIO(file_bytes))
        text = "\n".join(
            paragraph.text
            for paragraph in document.paragraphs
        )

    else:
        raise ValueError(
            "Unsupported file type. Upload PDF or DOCX."
        )

    text = text.strip()

    if not text:
        raise ValueError(
            "No extractable text found in this document."
        )

    return text


def split_text(text: str) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=3000,
        chunk_overlap=300,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    return [
        chunk
        for chunk in splitter.split_text(text)
        if chunk.strip()
    ]
