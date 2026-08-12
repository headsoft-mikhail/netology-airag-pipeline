# Description
## RAG Data Preparation Pipeline

Пайплайн подготовки документов для последующего использования в системах Retrieval-Augmented Generation (RAG).

Проект выполняет загрузку, parsing, очистку, нормализацию, дедупликацию, структурирование и экспорт документов в единый формат. Embeddings и vector database в рамках проекта не реализуются.

## Возможности

Pipeline поддерживает обработку документов следующих форматов:

* TXT
* JSON
* HTML

Реализованы:

* автоматическое обнаружение исходных файлов;
* parsing разных форматов;
* очистка текста;
* Unicode-нормализация;
* расчёт статистики документов;
* exact-дедупликация;
* near-duplicate detection с использованием MinHash;
* формирование единой структуры документов;
* расширенная metadata;
* экспорт в JSON и JSONL;
* manifest запуска;
* логирование этапов обработки;
* воспроизводимый запуск через YAML-конфигурацию.
* sentence-based, paragraph-based и token/text chunking;
* overlap между соседними чанками;
* token-aware ограничение размера чанков;
* validation чанков;
* metadata и lineage для чанков;
* расчёт embeddings для подготовленных chunks;
* validation embeddings;
* сохранение метаданных embedding;
* manifest для embeddings-pipeline.

## Структура проекта

```
project/
├── Justfile
├── README.md
├── config
│   └── default.yaml
├── data
│   ├── chunks
│   │   ├── chunks.json
│   │   ├── chunks.jsonl
│   │   └── manifest.json
│   ├── embeddings
│   │   ├── embeddings.json
│   │   ├── embeddings.jsonl
│   │   └── manifest.json
│   ├── prepared
│   │   ├── dataset.json
│   │   ├── dataset.jsonl
│   │   └── manifest.json
│   └── raw
│       ├── backup_guide.txt
│       ├── cpu_installation.txt
│       ├── faq.json
│       ├── memory_installation.txt
│       ├── network_setup.txt
│       ├── software_update.json
│       ├── ssd_guide.txt
│       ├── support_article.html
│       ├── support_article_duplicate.html
│       ├── support_article_near_duplicate.html
│       ├── system_requirements.html
│       └── troubleshooting.json
├── pyproject.toml
├── src
│   ├── __init__.py
│   └── rag
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── config.py
│       ├── manifest.py
│       ├── models.py
│       └── pipelines
│           ├── chunk
│           │   ├── __init__.py
│           │   ├── pipeline.py
│           │   └── stages
│           │       ├── __init__.py
│           │       ├── exporter.py
│           │       ├── loader.py
│           │       ├── splitter.py
│           │       └── validator.py
│           ├── embeddings
│           │   ├── __init__.py
│           │   ├── pipeline.py
│           │   └── stages
│           │       ├── __init__.py
│           │       ├── embedding.py
│           │       ├── exporter.py
│           │       ├── loader.py
│           │       └── validator.py
│           └── prepare
│               ├── __init__.py
│               ├── pipeline.py
│               └── stages
│                   ├── __init__.py
│                   ├── cleaner.py
│                   ├── deduplication.py
│                   ├── exporter.py
│                   ├── loader.py
│                   ├── normalizer.py
│                   ├── parser.py
│                   └── structurer.py
└── uv.lock
```

## Этапы prepare-pipeline

Pipeline состоит из последовательных этапов.
```
Raw documents
     │
     ▼
  Loading    
     │
     ▼
  Parsing
     │
     ▼
  Cleaning
     │
     ▼
Normalization
     │
     ▼
Deduplication
     │
     ▼
Structuring
     │
     ▼
   Export
     │
     ▼
Prepared dataset
```
----
### Loading

На первом этапе pipeline находит документы в data/raw, определяет их тип и загружает содержимое.

Для каждого документа формируется единое внутреннее представление с информацией об источнике и типе файла.

----
### Parsing

В зависимости от типа файла используется соответствующий parser:

* TXT — чтение текстового содержимого;
* JSON — преобразование структурированных данных в читаемый текст;
* HTML — извлечение текста с помощью BeautifulSoup.

При обработке HTML удаляются служебные элементы:

* script;
* style;
* nav;
* footer.

----
### Cleaning

На этапе очистки удаляются:
* управляющие символы;
* лишние пробелы;
* лишние пустые строки;
* ненужные пробелы вокруг переносов строк.

Также нормализуются переносы строк.

Цель этапа — получить читаемый текст без изменения его смыслового содержания.

----
### Normalization

Выполняется единая нормализация всех документов:

* Unicode normalization;
* нормализация пробелов;
* нормализация табуляции;
* расчёт статистики текста.

Для каждого документа рассчитываются:

* количество символов;
* количество слов;
* количество предложений.

----
### Deduplication

Реализованы два уровня дедупликации.

#### Exact duplicates

Для текста вычисляется SHA-256 hash.

Если два документа имеют одинаковый hash, второй документ удаляется.

#### Near duplicates

Для обнаружения похожих документов используется MinHash из библиотеки datasketch.

В конфигурации задаётся порог сходства:

deduplication:
  similarity_threshold: 0.65

Документы с similarity выше заданного порога считаются near-duplicates и удаляются.

----
### Structuring

После обработки документы приводятся к единому формату:
```json
{
  "text": "...",
  "metadata": {
    "source": "data/raw/example.txt",
    "file_type": "txt",
    "document_id": "...",
    "section": [],
    "character_count": 1000,
    "word_count": 150,
    "sentence_count": 10
  }
}
```

document_id формируется детерминированно на основе источника документа.

----
### Export

Подготовленные документы сохраняются в `data/prepared/`

Pipeline создаёт два формата:
- dataset.json
- dataset.jsonl

Также формируется:
- manifest.json
с информацией о результате запуска.

## Этапы chunk-pipeline
```
Prepared documents
       │
       ▼
    Loading
       │
       ▼
    Splitting
       │
       ▼
   Validation
       │
       ▼
    Export
       │
       ▼
     Chunks
```
----
### Loading

На этапе Loading pipeline загружает подготовленные документы из `data/prepared/documents.jsonl` и преобразует их во внутренние модели.

---

### Splitting

На этапе Splitting текст документов разбивается на chunks с использованием выбранной стратегии chunking.

Поддерживаются стратегии:

* `sentence`;
* `paragraph`;
* `token` / `text`.

При разбиении учитываются размер chunk, token budget и overlap.

---

### Validation

На этапе Validation выполняется проверка сформированных chunks: наличие текста, корректность metadata, размера, идентификаторов, связи с исходным документом и overlap.

Результаты проверки сохраняются в виде validation metrics.

---

### Export

На этапе Export chunks сохраняются в `data/chunks/` в форматах:

* `chunks.json`;
* `chunks.jsonl`.

---

### Chunks

Результатом pipeline является набор chunks с metadata, подготовленный для дальнейшего embeddings-этапа.

---

### Manifest

На этапе Manifest формируется `manifest.json` с информацией о запуске, конфигурации, количестве chunks и результатах validation, с учетом manifest prepare-пайплайна.

## Этапы embeddings-pipeline
```
     Chunks
       │
       ▼  
    Loading  
       │  
       ▼  
Embedding model  
       │
       ▼  
   Validation  
       │  
       ▼
     Export  
       │
       ▼
   Embeddings
```
----
### Loading

На этапе Loading pipeline загружает chunks из data/chunks/chunks.jsonl и преобразует их во внутренние модели. Для каждого chunk сохраняются исходный текст, идентификатор и metadata, необходимые для последующего связывания chunk с рассчитанным embedding.

---

### Embedding

На этапе Embedding для каждого chunk рассчитывается embedding с использованием выбранной embedding-модели.  
Модель и её основные параметры задаются через конфигурацию pipeline.  
Результатом обработки является embedding-вектор, связанный с исходным chunk через его metadata.  
Поддерживается использование локальной embedding-модели.  
Для каждого результата сохраняется:
* исходный текст chunk;
* embedding-вектор;
* идентификатор исходного документа;
* идентификатор и metadata chunk;
* название embedding-модели;
* размерность embedding-вектора.

---

### Validation

На этапе Validation выполняется проверка рассчитанных embeddings.  
Проверяется:
* наличие embedding для каждого chunk;
* отсутствие пустых embedding;
* наличие идентификаторов chunks;
* корректность связи embedding с исходным chunk;
* одинаковая размерность всех embedding-векторов;
* соответствие фактической размерности размерности, заявленной моделью;
* отсутствие некорректных значений в embedding.

Результаты проверки сохраняются в виде validation metrics.

---

### Export

На этапе Export результаты embeddings сохраняются в data/embeddings/.  
Pipeline создаёт файлы:
* embeddings.json
* embeddings.jsonl
Каждая строка jsonl содержит один chunk, его embedding и metadata. Файл предназначен для последующего использования на этапе загрузки данных в vector store.

---

### Manifest

После выполнения pipeline формируется manifest.json. Manifest содержит информацию о предыдущем этапе pipeline и результаты текущего запуска


## Конфигурация

Основные параметры pipeline находятся в `config/default.yaml`. 
В конфигурации задаются пути к исходным и подготовленным данным, параметры дедупликации, настройки экспорта, чанкинга, эмбеддинга.

Параметры не хранятся непосредственно в коде, что позволяет изменять поведение pipeline без изменения исходных файлов.

## Исходные данные

Для тестового набора используется 12 исходных документов.

В набор специально включены:
* документы разных форматов;
* exact duplicate;
* near-duplicate.

Из 12 исходных документов после дедупликации в итоговый датасет попадает 10 документов.

Pipeline не требует ручного изменения исходных документов перед повторным запуском.
Повторный запуск перезаписывает подготовленный датасет и manifest.

Идентификаторы документов формируются детерминированно, поэтому при одинаковых входных данных структура и результаты обработки остаются одинаковыми.

## Ограничения

Проект предназначен для демонстрации этапов подготовки данных перед RAG.

В текущей версии не реализованы:

* vector database;
* PDF parsing;
* API sources;
* semantic search;
* LLM-based document processing.

Расчёт embeddings реализован как отдельный pipeline после подготовки и chunking документов.  

Следующим этапом обработки может быть загрузка полученных embeddings в vector store и реализация semantic search

# Установка и запуск
# Project dev environment (uv + just)

Local development stack for ML workflows with:
- Управление версией python и окружением: `uv` + `pyenv`
- Автоматизация команд: `just`

```bash
just setup && just python 3.13 && just lock && just install
```


## Запуск
Pipeline запускается из корня проекта:
```bash
just rag_prepare && just rag_chunk && just reg_embegging
```
После выполнения результаты наxодятся в
```
data/prepared/
data/chunks/
data/embeddings/
```