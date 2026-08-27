# Description
## RAG Pipeline
Пайплайн подготовки документов для последующего использования в системах Retrieval-Augmented Generation (RAG).

Проект выполняет загрузку, parsing, очистку, нормализацию, дедупликацию, структурирование, разбиение документов на chunks, расчёт embeddings и загрузку данных в vector store.

После подготовки vector store отдельный evaluation-модуль выполняет retrieval по пользовательскому запросу, формирует контекст, передаёт его в LLM и сохраняет результаты тестовых запросов.

## Содержание
- [Возможности](#Возможности)
- [Структура проекта](#Структура-проекта)
- [Этапы prepare-pipeline](#Этапы-prepare-pipeline)
- [Этапы chunk-pipeline](#Этапы-chunk-pipeline)
- [Этапы embeddings-pipeline](#Этапы-embeddings-pipeline)
- [Этапы vector-store-pipeline](#Этапы-vector-store-pipeline)
- [Этапы evaluation](#Этапы-evaluation)
- [Оптимизация RAG](#Оптимизация-RAG)
- [Конфигурация](#Конфигурация)
- [Исходные данные](#Исходные-данные)
- [Установка и запуск](#Установка-и-запуск)

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
* воспроизводимый запуск через YAML-конфигурацию;
* sentence-based, paragraph-based и token/text chunking;
* overlap между соседними чанками;
* token-aware ограничение размера чанков;
* validation чанков;
* metadata и lineage для чанков;
* расчёт embeddings для подготовленных chunks;
* validation embeddings;
* сохранение метаданных embedding;
* manifest для embeddings-pipeline;
* загрузка готовых embeddings в vector store;
* создание и пересоздание коллекции Qdrant;
* batch-загрузка vectors и metadata;
* validation загруженных данных;
* тестовый similarity search;
* manifest для vector-store-pipeline;
* retrieval пользовательского запроса;
* формирование контекста из найденных chunks;
* запрос к LLM;
* интерактивный режим получения ответа;
* автоматический прогон тестовых вопросов и формирование evaluation report;
* логирование chunks, использованных для формирования контекста, и сохранение результатов retrieval в evaluation report.

## Структура проекта

```
project/
├── Justfile
├── README.md
├── config
│   ├── evaluate.yaml
│   └── pipeline.yaml
├── data
│   ├── chunks
│   │   ├── chunks.json
│   │   ├── chunks.jsonl
│   │   └── manifest.json
│   ├── embeddings
│   │   ├── embeddings.json
│   │   ├── embeddings.jsonl
│   │   └── manifest.json
│   ├── evaluation
│   │   ├── evaluation_test.json
│   │   └── evaluation_test_baseline.json
│   ├── prepared
│   │   ├── dataset.json
│   │   ├── dataset.jsonl
│   │   └── manifest.json
│   ├── raw
│   │   ├── backup_guide.txt
│   │   ├── cpu_installation.txt
│   │   ├── faq.json
│   │   ├── memory_installation.txt
│   │   ├── network_setup.txt
│   │   ├── security_policy.txt
│   │   ├── software_update.json
│   │   ├── ssd_guide.txt
│   │   ├── support_article.html
│   │   ├── support_article_duplicate.html
│   │   ├── support_article_near_duplicate.html
│   │   ├── system_requirements.html
│   │   ├── troubleshooting.json
│   │   ├── warranty_policy.txt
│   │   └── warranty_policy_new.txt
│   └── vector_store
│       ├── collection
│       │   └── rag_chunks
│       │       └── storage.sqlite
│       ├── manifest.json
│       ├── meta.json
│       └── search_results.json
├── pyproject.toml
├── src
│   ├── __init__.py
│   ├── evaluation
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   ├── cli.py
│   │   ├── config.py
│   │   ├── context_builder.py
│   │   ├── evaluator.py
│   │   ├── llm_client.py
│   │   └── retrieval_client.py
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
│           ├── prepare
│           │   ├── __init__.py
│           │   ├── pipeline.py
│           │   └── stages
│           │       ├── __init__.py
│           │       ├── cleaner.py
│           │       ├── deduplication.py
│           │       ├── exporter.py
│           │       ├── loader.py
│           │       ├── normalizer.py
│           │       ├── parser.py
│           │       └── structurer.py
│           └── vector_store
│               ├── __init__.py
│               ├── pipeline.py
│               └── stages
│                   ├── __init__.py
│                   ├── exporter.py
│                   ├── loader.py
│                   ├── search.py
│                   ├── store.py
│                   └── validator.py
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

На этапе Loading pipeline загружает подготовленные документы из `data/prepared/dataset.jsonl` и преобразует их во внутренние модели.

---

### Splitting

На этапе Splitting текст документов разбивается на chunks с использованием выбранной стратегии chunking.

Поддерживаются стратегии:

* `sentence`;
* `paragraph`;
* `token` / `text`.

При разбиении учитываются размер chunk, token budget и overlap.

Для текущей базы знаний используется `chunk_size: 220` и `chunk_overlap: 50`. Размер 220 токенов выбран так, чтобы chunk обычно содержал законченную инструкцию или несколько связанных предложений, но не объединял слишком много разных фактов. Overlap 50 токенов сохраняет смысловую связь между соседними chunks и снижает риск потери факта на границе разбиения. При этом overlap остаётся существенно меньше размера chunk и не приводит к чрезмерному дублированию контекста.

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


## Этапы vector-store-pipeline
```
   Embeddings
       │
       ▼
    Loading
       │
       ▼
  Vector Store
       │
       ▼
   Validation
       │
       ▼
     Search
       │
       ▼
   Artifacts
```

### Loading

На этапе Loading pipeline загружает готовые embeddings из data/embeddings/embeddings.jsonl. Записи преобразуются во внутренние модели и передаются в vector store

---

### Vector Store

В качестве vector store используется Qdrant.

Qdrant выбран для хранения embedding-векторов вместе с payload, содержащим текст chunk и его metadata. Это позволяет выполнять similarity search и одновременно получать информацию об исходном chunk.

Почему Qdrant

Выбран Qdrant, поскольку он сочетает простой локальный запуск, similarity search и хранение embedding вместе с metadata (payload).

В отличие от FAISS, Qdrant предоставляет полноценное хранилище с metadata и коллекциями. Chroma также подходит для локального RAG, но Qdrant удобнее для явного управления размерностью vectors, distance metric и batch-загрузкой. Milvus для небольшого учебного проекта избыточен, а pgvector имеет смысл преимущественно при наличии PostgreSQL-инфраструктуры.

Для данного проекта Qdrant является оптимальным вариантом по соотношению простоты и возможностей.

На этапе создания коллекции задаются:

* название коллекции;
* размерность vectors;
* distance metric;
* режим пересоздания коллекции.

Embeddings загружаются batch-ами.

Для каждой записи в Qdrant сохраняются:

* embedding-вектор;
* идентификатор chunk;
* текст chunk;
* идентификатор документа;
* source;
* metadata;
* информация об embedding-модели и её размерности.

Идентификатор точки Qdrant формируется отдельно на основе идентификатора chunk, поэтому исходный chunk_id сохраняется в payload.

---

### Validation

После загрузки выполняется проверка корректности индекса.

Проверяется:

* количество embeddings во входном файле;
* количество points в коллекции;
* совпадение количества входных embeddings и сохранённых points;
* корректность размерности vectors;
* отсутствие пустых vectors;
* отсутствие некорректных значений;
* наличие текста;
* наличие chunk_id;
* наличие document_id;
* наличие metadata.

Результаты проверки сохраняются в виде validation metrics.
Отдельный validation.json для этого стейджа не создается, результат валидации сохраняется в `data/vector_store/manifest.json`

---

### Search

После загрузки выполняются тестовые similarity search-запросы.

Для тестовых запросов используются существующие embeddings из входного файла, поэтому повторно рассчитывать embedding не требуется.

Для каждого запроса сохраняются:

* идентификатор тестового chunk;
* текст запроса;
* найденные chunks;
* score;
* идентификаторы найденных chunks;
* metadata найденных результатов.

Результаты сохраняются в `data/vector_store/search_results.json`

---

### Manifest

После выполнения pipeline формируется manifest.json.

Manifest содержит информацию о предыдущих этапах пайплайна и текущем запуске vector-store-pipeline.

---

## Этапы evaluation

Evaluation не является частью основного data preparation pipeline.
Он запускается после построения vector store и использует уже подготовленную базу знаний.
Назначение evaluation-модуля — проверить полный RAG-процесс:
```
    User query
        │
        ▼
  Query embedding
        │
        ▼
    Retrieval
        │
        ▼
   Top-k chunks
        │
        ▼
  Context builder
        │
        ▼
      Prompt
        │
        ▼
       LLM
        │
        ▼
      Answer
```

Evaluation реализован отдельно от rag.pipelines, поскольку он не изменяет и не подготавливает данные. Он использует результат работы pipeline как входной ресурс.

---

### Retrieval

RetrievalClient принимает пользовательский текстовый запрос.

Сначала запрос преобразуется в embedding с использованием той же embedding-модели, которая использовалась при индексации chunks.

После этого выполняется similarity search в vector_store.


---

### Context Builder

Найденные chunks объединяются в единый контекст для LLM.

Каждый fragment отделяется от остальных и содержит информацию об источнике

---

### LLM

Для генерации ответа используется LLM через Groq API.

Prompt содержит:

* системную инструкцию;
* найденный контекст;
* вопрос пользователя.

Модель должна отвечать только на основании переданного контекста.

Если в контексте отсутствует необходимая информация, модель должна сообщить, что информации недостаточно, вместо генерации неподтверждённого ответа.

API key передаётся через переменную окружения `GROQ_API_KEY` в файле `.env`.
Файл `.env` включён в `.gitignore`, перед запуском evaluation необходимо создать в корне проекта файл `.env`:
```env
GROQ_API_KEY=ваш_ключ_Groq_API
```



---

## Оптимизация RAG

Для полноценного улучшения необходим сбор статистики: реальные вопросы пользователей и ответы RAG. По текущим тестовым вопросам модель отрабатывает корректно благодаря имеющимся возможностям и уже проделанному подбору параметров на предыдущих этапах.

### На этапе prepare:
- нормализация текста с возможностью настройки способа нормализации
- очистка от служебных символов и разметки
- дедупликация точных копий с возможностью отключения дедупликации
- дедупликация похожих файлов по настраиваемому порогу и с возможностью отключения дедупликации

### На этапе chunk:
- выбор способа разделения на чанки: token, sentence, paragraph
- настраиваемый размер чанков
- настраиваемый overlap чанков

### На этапе embedding:
- настраиваемая модель для embedding

### На этапе поиска в vector-store:
- настраиваемая модель для подготовки embedding запроса
- настраиваемое значение top_k
- фильтрация по метаданным чанков (возможность исключить документы по настраиваемому списку)

### На этапе подготовки контекста:
- фильтрация по значению score

### На этапе запроса в LLM:
- выбор модели
- в промпте прямо указано использовать только контекст
- в промпте прямо указано, что делать, если данных в контексте недостаточно

### Сравнение baseline и оптимизированной версии

Отчёт baseline находится в `/data/evaluation/evaluation_test_baseline.json`, отчёт после оптимизации — в `/data/evaluation/evaluation_test.json`.

Проблемы:
- near-deduplication: false - в top_k попали почти одинаковые чанки из разных документов
- стратегия чанкинга: token - обрезка чанка в любом месте
- top_k = 5, но используются чаще всего только первые 2, остальные чанки - лишняя нагрузка на LLM
- нет фильтрации при поиске - старый неактуальный документ нужно исключать из поиска
- нет инструкции для LLM в случае отсутствия ответа в контексте

Что изменено:
- Включена near-deduplication: false -> true
- Изменена стратегия чанкинга: token -> sentence
- Уменьшено количество передаваемых в LLM чанков 5 -> 3
- Добавлена фильтрация по значению score - но score довольно высокий для всех результатов, в том числе из-за уменьшения top_k
- Включена фильтрация неактуальных документов: поиск не ведется по чанкам устаревшего документа data/raw/warranty_policy.txt
- Добавлена инструкция для LLM при отсутствии контекста

Тестовый набор содержит пять вопросов с прямым ответом, один составной вопрос, требующий нескольких фрагментов, один расширенный вопрос и два вопроса без прямого ответа в базе знаний. Составной вопрос о частоте резервного копирования требует объединить правила ежедневного копирования критических данных из `security_policy.txt` и еженедельного копирования важных данных из `backup_guide.txt`.

| Вопрос и тип | Ключевые факты ожидаемого ответа | Ожидаемый источник | Найденные источники baseline | Ответ baseline | Найденные источники после оптимизации | Ответ после оптимизации | Комментарий |
|---|---|---|---|---|---|---|---|
| Какой гарантийный срок на оборудование?<br>Прямой ответ | Основное оборудование — 36 месяцев | `warranty_policy_new.txt` | `warranty_policy_new.txt`, `warranty_policy.txt` | 36 месяцев | `warranty_policy_new.txt` | 36 месяцев | Устаревший документ исключён из retrieval |
| Какое время понадобится на диагностику?<br>Прямой ответ | Стандартный срок первичной проверки — 7 рабочих дней | `warranty_policy_new.txt` | `warranty_policy_new.txt`, `warranty_policy.txt` | 10 рабочих дней | `warranty_policy_new.txt`, `memory_installation.txt` | 7 рабочих дней | После фильтрации использован актуальный источник; последний найденный chunk нерелевантен |
| Сколько стоит доставка в сервисный центр?<br>Без прямого ответа | Фиксированная стоимость доставки не указана; клиент оплачивает её самостоятельно, возможна компенсация 20 евро | — | `warranty_policy_new.txt`, `warranty_policy.txt` | 15 евро | `warranty_policy_new.txt` | Ответ не найден | Неактуальная цена больше не возвращается; точной стоимости в актуальной базе нет |
| Как часто должны создаваться резервные копии?<br>Составной, несколько фрагментов | Критические данные — ежедневно в 02:00 UTC; важные данные — не реже одного раза в неделю | `security_policy.txt`, `backup_guide.txt` | `backup_guide.txt`, `security_policy.txt` | Ежедневно для критических данных и еженедельно для остальных | `security_policy.txt`, `backup_guide.txt` | Не реже одного раза в неделю | Retrieval корректно нашёл оба необходимых источника, но LLM сформулировала неполный ответ и пропустила правило ежедневного копирования критических данных. Более полный ответ baseline был получен случайно: baseline prompt не содержал требования учитывать все релевантные факты. Для стабильного результата требуется доработка prompt, обязывающая модель полностью отвечать на составные вопросы по всему переданному контексту |
| Как часто нужно менять пароль?<br>Прямой ответ | Срок действия пароля — 180 дней | `security_policy.txt` | `security_policy.txt`, `backup_guide.txt` | Каждые 180 дней | `security_policy.txt`, `backup_guide.txt` | Каждые 180 дней | Ответ корректен, но retrieval содержит нерелевантный источник |
| Сколько хранятся резервные копии?<br>Расширенный ответ | Ежедневные — 30 дней; еженедельные — 6 месяцев; ежегодные — 5 лет | `security_policy.txt` | `backup_guide.txt`, `security_policy.txt` | Сроки представлены подробной таблицей | `security_policy.txt`, `backup_guide.txt` | Еженедельные — 6 месяцев, ежегодные — 5 лет | Оптимизированный ответ не упомянул срок хранения ежедневных копий |
| Сколько стоит страхование жизни?<br>Без ответа | Информация отсутствует в базе знаний | — | `security_policy.txt`, `warranty_policy.txt`, `warranty_policy_new.txt` | Информация отсутствует | `security_policy.txt` | Ответ не найден | После оптимизации отсутствие ответа оформлено в заданном формате |
| Какие системные требования Desktop Support Tools?<br>Прямой ответ | Windows 10 22H2+, 64-битный двухъядерный CPU, 4 ГБ RAM, 2 ГБ на диске, 1280×720, интернет | `system_requirements.html` | `system_requirements.html`, `software_update.json`, `support_article.html`, `support_article_near_duplicate.html` | Корректный перечень требований | `system_requirements.html`, `software_update.json`, `support_article.html` | Корректный перечень требований | Near-deduplication исключила один повторяющийся документ |
| Как проверить версию Desktop Support Tools?<br>Прямой ответ | Открыть приложение и перейти в раздел «О программе» | `software_update.json` | `system_requirements.html`, `software_update.json` | Открыть раздел «О программе» | `system_requirements.html`, `software_update.json` | Открыть раздел «О программе» | Корректный ответ сохраняется при уменьшенном top-k |

### Возможные доработки:
- не всегда оптимальное разбиение на чанки. Есть слишком короткие чанки, не содержащие полезного смысла.  Решение - Внимательная доработка splitter для качественного разбиения, обработка разделов. Хотя на тестовых вопросах RAG все равно справился
- доработка prompt, чтобы исключить лишнюю информацию от LLM, такую как ссылка на раздел или добавление «Ответ:», и требовать полного учёта всех релевантных фактов из контекста при ответе на составные вопросы
- добавление механизма загрузки и сохранения метаданных документов (вместо списка исключений из поиска) для фильтрации при поиске
- при значительном изменении базы исходных документов потребуется подобрать другие параметры пайплайна для получения хорошего качества работы RAG


## Конфигурация

Все параметры pipeline находятся в `config/pipeline.yaml`,  
В конфигурации задаются пути к исходным и подготовленным данным, параметры дедупликации, настройки экспорта, чанкинга, эмбеддинга, vector-store.
  
Параметры evaluation находятся - в `config/evaluate.yaml`.

Параметры не хранятся непосредственно в коде, что позволяет изменять поведение pipeline и evaluation без изменения исходных файлов.

## Исходные данные

Для тестового набора используется 15 исходных документов.

В набор специально включены:
* документы разных форматов;
* exact duplicate;
* near-duplicate.

Из 15 исходных документов после дедупликации в итоговый датасет попадает 13 документов.
Повторный запуск перезаписывает подготовленный датасет и manifest.

Идентификаторы документов формируются детерминированно, поэтому при одинаковых входных данных структура и результаты обработки остаются одинаковыми.


# Установка и запуск
## Project dev environment (uv + just)

Local development stack for ML workflows with:
- Управление версией python и окружением: `uv` + `pyenv`
- Автоматизация команд: `just`

```bash
just setup && just python 3.13 && just lock && just install
```


## Запуск
**Pipeline** запускается из корня проекта:
```bash
just rag_prepare && just rag_chunk && just rag_embedding && just rag_vectorstore
```
или
```bash
just pipeline
```
После выполнения результаты находятся в
```
data/prepared/
data/chunks/
data/embeddings/
data/vector_store/
```

Запуск **Evaluation**:
Интерактивный режим для проверки произвольного пользовательского запроса
```bash
just evaluate "вопрос_в_кавычках"
```

Автоматический прогон заранее подготовленного набора тестовых вопросов
```bash
just evaluate_test
```
Для каждого тестового вопроса в evaluation report фиксируются:
* вопрос;
* top-k найденных chunks с metadata;
* значение `min_score` — минимальный score для отбора chunks при формировании контекста;
* сформированный контекст;
* ответ LLM.
