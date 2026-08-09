import dataclasses
import logging
import re
import typing
import unicodedata

from rag import models

LOGGER_OBJ: typing.Final = logging.getLogger(__name__)


@dataclasses.dataclass(kw_only=True, slots=True, frozen=True)
class TextNormalizer:
    unicode_form: typing.Literal["NFC", "NFD", "NFKC", "NFKD"] = "NFC"

    def normalize(self, document: models.ParsedDocument) -> models.ParsedDocument:
        LOGGER_OBJ.info(f"Normalizing {document.source}...")
        text = unicodedata.normalize(self.unicode_form, document.text)

        text = text.replace("\t", " ")
        text = re.sub(r" {2,}", " ", text)

        character_count: typing.Final = len(text)
        word_count: typing.Final = len(re.findall(r"\b\w+\b", text, re.UNICODE))
        sentence_count: typing.Final = len(re.findall(r"[.!?]+(?:\s|$)", text))

        return document.model_copy(
            update={
                "text": text,
                "character_count": character_count,
                "word_count": word_count,
                "sentence_count": sentence_count,
            }
        )
