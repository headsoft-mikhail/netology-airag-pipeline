import json
import logging
import typing
from pathlib import Path

from rag.models import PreparedDocument

LOGGER_OBJ: typing.Final = logging.getLogger(__name__)


def load_documents(input_path: Path) -> list[PreparedDocument]:
    documents: list[PreparedDocument] = []

    with input_path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue

            try:
                data = json.loads(line)
                document = PreparedDocument.model_validate(data)
            except (json.JSONDecodeError, ValueError) as exc:
                LOGGER_OBJ.error("Failed to load document at line %d: %s", line_number, exc)
                continue

            documents.append(document)

    LOGGER_OBJ.info("Loaded %d prepared documents.", len(documents))

    return documents