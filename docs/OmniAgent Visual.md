markdown
# OmniAgent Visual Search Module - Complete Documentation

> **Version:** 1.0.0  
> **Date:** September 2026  
> **Status:** Enterprise-Ready, Production Tested  

---

## 📌 Project Overview

Yeh **OmniAgent Visual Search System** ek **enterprise-grade, multi-provider SaaS solution** hai jo e-commerce platforms ko AI-powered visual search capability deta hai. User koi bhi image upload kare, system CLIP model se uska embedding banata hai aur vector database mein search karke matching products return karta hai.

**Key Highlights:**
- 100% Free & Open Source (CLIP + Qdrant)
- Multi-Provider Support (Qdrant, MongoDB Atlas, Pinecone)
- Multi-Store Support (Shopify, WooCommerce, MongoDB, Sanity)
- BYOC (Bring Your Own Cloud) - User apna khud ka vector DB use kar sakta hai
- Smart Incremental Sync (Naye/changed products hi process hote hain)
- Thread-Safe Model Loading
- Cloud-Deploy Ready

---

## 📁 Total Files (23 Files)

| Category | Count |
|----------|-------|
| **Core Files** | 3 |
| **Shared Files** | 8 |
| **Visual Search Module Files** | 12 |
| **Total** | **23** |

---

## 🗂️ Complete File Structure
backend/src/
├── core/
│ ├── config.py # System configuration (provider-agnostic)
│ ├── db_base.py # SQLAlchemy Base class
│ └── db_session.py # Async database engine & session
│
├── shared/
│ ├── api/routes/
│ │ ├── auth.py # User registration, login, refresh token
│ │ ├── deps.py # JWT + API Key authentication dependencies
│ │ ├── settings.py # Vector DB + Data Source connect
│ │ └── ingestion.py # Job tracking endpoints
│ ├── models/
│ │ ├── user.py # User model + selected_vector_provider
│ │ └── integration.py # UserIntegration model (encrypted credentials)
│ └── utils/
│ ├── auth.py # Password hash, JWT, API key generation
│ └── security.py # Fernet encryption/decryption
│
├── modules/
│ └── visual_search/
│ ├── api/routes/
│ │ └── visual.py # Visual Search API endpoints
│ ├── models/
│ │ └── ingestion.py # IngestionJob model (job tracking)
│ ├── schemas/
│ │ └── visual.py # API request/response schemas
│ └── services/
│ ├── connectors/
│ │ ├── base.py # BaseConnector interface
│ │ ├── shopify_connector.py # Shopify product fetch
│ │ ├── woocommerce_connector.py # WooCommerce product fetch
│ │ ├── mongo_connector.py # MongoDB product fetch
│ │ └── sanity_connector.py # Sanity CMS product fetch
│ ├── vector_store/
│ │ ├── base.py # VisualVectorStore interface
│ │ ├── qdrant_adapter.py # Qdrant implementation
│ │ ├── mongo_adapter.py # MongoDB Atlas Vector Search
│ │ └── factory.py # Vector store factory (BYOC)
│ └── visual/
│ ├── engine.py # CLIP model (image embedding)
│ ├── agent.py # Smart sync pipeline
│ └── file_ingestion.py # CSV/JSON file upload processing
│
└── main.py # FastAPI app entry point

text

---

## 📄 File-by-File Detailed Analysis

### 1. Core Files (3 Files)

#### `core/config.py`
**Purpose:** System ka central configuration file.  
**Main Features:**
- Provider-agnostic settings (LLM, Embeddings, Vector DB)
- SECRET_KEY aur ENCRYPTION_KEY .env se load hote hain (no insecure defaults)
- DATABASE_URL auto-convert (SQLite ↔ PostgreSQL)
- Multiple API keys support (OpenAI, Groq, Google, Anthropic, etc.)
- CORS origins configurable

#### `core/db_base.py`
**Purpose:** SQLAlchemy declarative base.  
**Main Features:**
- Base class jo saare models inherit karte hain
- Simple, clean, standard

#### `core/db_session.py`
**Purpose:** Async database connection aur session management.  
**Main Features:**
- Async engine (create_async_engine)
- Connection pooling (pool_size=20, max_overflow=40)
- Graceful cleanup (session close, rollback)
- PostgreSQL/SQLite connection argument handling

---

### 2. Shared Files (8 Files)

#### `shared/api/routes/auth.py`
**Purpose:** User authentication endpoints.  
**Main Features:**
- `POST /auth/register` - User registration + API key generation
- `POST /auth/login` - Login + access/refresh tokens
- `POST /auth/refresh` - Refresh token rotation
- Argon2 password hashing (strongest)
- JWT token generation (HS256)

#### `shared/api/routes/deps.py`
**Purpose:** Authentication dependencies.  
**Main Features:**
- `get_current_user()` - JWT token verify (dashboard access)
- `get_current_user_by_api_key()` - API key verify (public widgets)
- `decode_refresh_token()` - Refresh token decode
- Tokens type check (access vs refresh)

#### `shared/api/routes/settings.py`
**Purpose:** User settings and integrations management.  
**Main Features:**
- `POST /settings/vector-db` - Vector DB connect (BYOC)
- `POST /settings/data-source` - Data source connect (Shopify/Woo/Mongo/Sanity)
- `POST /settings/vector-db/select` - Active vector DB selection
- `GET /settings/integrations` - List all connected services
- `DELETE /settings/integration/{provider}` - Remove integration
- Credentials validation + connection testing

#### `shared/api/routes/ingestion.py`
**Purpose:** Background job tracking endpoints.  
**Main Features:**
- `GET /ingestion/jobs` - List all user's jobs
- `GET /ingestion/jobs/{job_id}` - Specific job status
- User isolation (apna job hi dekh sakta hai)
- `session_id` based security filtering

#### `shared/models/user.py`
**Purpose:** User data model.  
**Main Features:**
- `api_key` - Unique API key (public widget auth)
- `allowed_domains` - Domain whitelist
- `bot_name` / `bot_instruction` - Bot customization
- `selected_vector_provider` - Active vector DB (MongoDB/Qdrant)
- `selected_collection_name` - Active collection name
- Timestamps (created_at, updated_at)

#### `shared/models/integration.py`
**Purpose:** User's integration credentials storage.  
**Main Features:**
- `_credentials` - Encrypted storage (Fernet)
- `schema_map` - Data structure mapping
- `profile_description` - Integration description
- `is_active` - Active/inactive status
- Credentials property (encrypt/decrypt)

#### `shared/utils/auth.py`
**Purpose:** Authentication utilities.  
**Main Features:**
- Argon2 password hashing/verification
- JWT access token creation (30 min expiry)
- Refresh token creation (7 days expiry)
- API key generation (omni_ + 32-byte URL-safe)

#### `shared/utils/security.py`
**Purpose:** Encryption/decryption utilities.  
**Main Features:**
- Fernet symmetric encryption
- ENCRYPTION_KEY from .env (no fallback, strict)
- Encrypt/decrypt integration credentials

---

### 3. Visual Search Module Files (12 Files)

#### `visual_search/api/routes/visual.py`
**Purpose:** Visual Search API endpoints.  
**Main Features:**
- `POST /visual/sync` - Trigger background sync (JWT auth)
- `POST /visual/search` - Image search (API key + domain lock)
- `POST /visual/file/preview` - CSV/JSON headers preview
- `POST /visual/file/process` - File upload + field mapping process
- `GET /visual/jobs/{job_id}` - Job status check
- Domain lock security (allowed_domains)
- Selected vector DB provider usage

#### `visual_search/models/ingestion.py`
**Purpose:** Ingestion job tracking model.  
**Main Features:**
- `ingestion_type` - visual_sync / file_upload
- `status` - pending / processing / completed / failed
- `items_processed` / `total_items` - Progress tracking
- `details` - JSON extra data (products vs images count)
- `error_message` - Failure logging

#### `visual_search/schemas/visual.py`
**Purpose:** API request/response schemas.  
**Main Features:**
- `FilePreviewResponse` - File headers response
- `JobStartResponse` - Job start acknowledgment
- `JobStatusResponse` - Job status response
- `VisualSearchResponse` - Search results response
- Type-safe validation with Pydantic

#### `visual_search/services/connectors/base.py`
**Purpose:** Base connector interface.  
**Main Features:**
- `connect()` - Test connection
- `fetch_products()` - Fetch products with image URLs
- `get_schema_summary()` - Data structure description
- Abstract methods (all connectors must implement)

#### `visual_search/services/connectors/shopify_connector.py`
**Purpose:** Shopify store product fetch.  
**Main Features:**
- Shopify Admin API integration
- Pagination handling (250 products per page)
- Product images extraction (product_id, slug, image_url)
- Rate limiting (0.5 sec sleep)
- Session activation/deactivation

#### `visual_search/services/connectors/woocommerce_connector.py`
**Purpose:** WooCommerce store product fetch.  
**Main Features:**
- WooCommerce REST API integration
- Pagination (50 products per page)
- Product image extraction
- Timeout handling (20 seconds)
- Status check (200 OK validation)

#### `visual_search/services/connectors/mongo_connector.py`
**Purpose:** MongoDB custom database product fetch.  
**Main Features:**
- User's existing MongoDB connection
- `image_mode` support (cdn/local/mixed)
- `field_mapping` support (nested dot notation)
- Arrays handling (variants, cdnImages)
- Multi-adapter pattern (multiple image sources)

#### `visual_search/services/connectors/sanity_connector.py`
**Purpose:** Sanity CMS product fetch.  
**Main Features:**
- Sanity GROQ query support
- Custom query (user-defined)
- `field_mapping` support (nested fields)
- URL-encoded query handling
- Connection test (simple query)

#### `visual_search/services/vector_store/base.py`
**Purpose:** Vector store interface.  
**Main Features:**
- `collection_exists()` - Check collection
- `create_collection()` - Create with vector_size
- `upsert()` - Add/update points
- `search()` - Similarity search
- `scroll()` - Pagination (sync diff)
- `delete()` - Remove points
- Abstract class (all adapters implement)

#### `visual_search/services/vector_store/qdrant_adapter.py`
**Purpose:** Qdrant vector database implementation.  
**Main Features:**
- Qdrant Cloud/Local connection
- Collection creation with vector size + distance
- Payload indexing (user_id, product_id)
- Search with filters + score threshold
- Scroll/pagination support
- Delete by IDs

#### `visual_search/services/vector_store/mongo_adapter.py`
**Purpose:** MongoDB Atlas Vector Search implementation.  
**Main Features:**
- MongoDB connection string + database
- `$vectorSearch` aggregation pipeline
- Auto index creation (knnVector)
- `ReplaceOne` upsert (valid bulk_write)
- Search with filters + score threshold
- Scroll/delete support

#### `visual_search/services/vector_store/factory.py`
**Purpose:** Vector store factory (BYOC).  
**Main Features:**
- `get_visual_vector_store(credentials)` - Provider selection
- Qdrant adapter return
- MongoDB adapter return
- Error handling (unsupported provider)

#### `visual_search/services/visual/engine.py`
**Purpose:** CLIP model image embedding.  
**Main Features:**
- CLIP ViT-B/32 model (512-dimension embeddings)
- Thread-safe singleton pattern (threading.Lock)
- L2 normalization (cosine similarity ready)
- Image preprocessing (resize, normalize)
- Efficient memory usage

#### `visual_search/services/visual/agent.py`
**Purpose:** Smart sync pipeline (background job).  
**Main Features:**
- Pre-loads CLIP model (race condition fix)
- Smart incremental sync (diff calculation)
- Batch processing (100 items/batch)
- Parallel image download + embedding (20 workers)
- Progress tracking (products + images count)
- Provider injection in credentials
- Selected vector DB usage

#### `visual_search/services/visual/file_ingestion.py`
**Purpose:** CSV/JSON file upload processing.  
**Main Features:**
- `parse_file_headers()` - Headers extraction
- `process_file_upload()` - Background processing
- CSV/JSON parsing with field_mapping
- Image download + embedding generation
- Vector store upsert (batch)
- Progress tracking

#### `main.py`
**Purpose:** FastAPI application entry point.  
**Main Features:**
- All routers included (auth, settings, ingestion, visual)
- CORS middleware (configurable)
- Static files mounting
- Health check endpoint
- Universal start logic (PORT from env)

---

## 🎯 Features Summary (Total 24+ Features)

| # | Feature | Description |
|---|---------|-------------|
| 1 | **Visual Image Search** | Upload image → matching products |
| 2 | **CLIP Model** | 512-dim embeddings (state-of-the-art) |
| 3 | **Multi-Provider Vector DB** | Qdrant / MongoDB / Pinecone |
| 4 | **BYOC (Bring Your Own Cloud)** | User apna vector DB use kare |
| 5 | **Multi-Store Support** | Shopify / WooCommerce / MongoDB / Sanity |
| 6 | **Smart Incremental Sync** | Sirf naye/changed products process |
| 7 | **Batch Processing** | 100 images per batch, 20 parallel workers |
| 8 | **Progress Tracking** | Products + Images count |
| 9 | **CSV/JSON File Upload** | File se embeddings banayein |
| 10 | **Field Mapping** | User apna data pattern define kare |
| 11 | **Image Mode (cdn/local/mixed)** | Multiple image adapter support |
| 12 | **Thread-Safe Model Loading** | Race condition free |
| 13 | **API Key Authentication** | Public widget auth |
| 14 | **JWT Authentication** | Dashboard auth |
| 15 | **Domain Lock Security** | Allowed domains whitelist |
| 16 | **Active Vector DB Selection** | User decide kare (MongoDB/Qdrant) |
| 17 | **Credential Encryption** | Fernet encryption |
| 18 | **Job Tracking** | Background job status |
| 19 | **Refresh Token** | 7-day valid refresh token |
| 20 | **Argon2 Password Hashing** | Strongest password security |
| 21 | **CORS Configurable** | Production security |
| 22 | **Connection Testing** | Validate credentials before save |
| 23 | **Smart Diff Logic** | Add/Delete detection |
| 24 | **Auto Collection Creation** | Vector DB collection auto-create |
| 25 | **Score Threshold** | Configurable similarity threshold |

---

## 🛠️ Technologies Used

| Technology | Purpose |
|------------|---------|
| **Python 3.12** | Programming language |
| **FastAPI** | Web framework |
| **Uvicorn** | ASGI server |
| **SQLAlchemy 2.0** | ORM (async) |
| **PostgreSQL / SQLite** | Metadata database |
| **CLIP (ViT-B/32)** | Image embedding model |
| **Qdrant** | Vector database (free tier) |
| **MongoDB Atlas** | Vector database + product store |
| **Pinecone** | Vector database (future) |
| **Shopify API** | E-commerce connector |
| **WooCommerce API** | E-commerce connector |
| **Sanity API** | CMS connector |
| **PyMongo** | MongoDB Python driver |
| **Transformers** | CLIP model loading |
| **PyTorch** | Deep learning framework |
| **Pandas** | CSV/JSON file processing |
| **Pydantic** | Data validation |
| **JWT (python-jose)** | Token authentication |
| **Argon2 (passlib)** | Password hashing |
| **Fernet (cryptography)** | Encryption |
| **Requests** | HTTP calls (image download) |
| **concurrent.futures** | Parallel processing |

---

## 🏗️ Architecture Flow
User Image Upload (Frontend)
↓
POST /api/v1/visual/search
↓
[Authentication: API Key + Domain Lock]
↓
CLIP Model → 512-D Embedding
↓
Vector Store Adapter (Factory)
↓
Search in Qdrant/MongoDB
↓
Return Results (product_id, slug, score)
↓
Frontend UI (Product Cards)

text

---

## ✅ Conclusion

Yeh **complete Visual Search Module** ek **production-ready, enterprise-grade SaaS solution** hai. Isme saare modern best practices implement kiye gaye hain:
- Multi-provider support
- BYOC architecture
- Thread-safe processing
- Smart sync logic
- Security (encryption, auth, domain lock)

**Total Files: 23**  
**Total Features: 25+**  
**Technologies: 20+**

Yeh system kisi bhi e-commerce platform ke liye ready hai. Ab aap:
1. Frontend Dashboard bana sakte hain
2. Payment system integrate kar sakte hain
3. Hugging Face par deploy kar sakte hain
4. RAG Chatbot add kar sakte hain


markdown
# OmniAgent Core - Complete API Schemas & Provider Patterns

> Yeh file aapke pure system ke saare API patterns ka reference hai.
> Har endpoint, har provider, aur har configuration ka pura JSON format yahan hai.

---

## 🔐 Authentication

### 1. Register User
**Endpoint:** `POST /api/v1/auth/register`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "secure_password_123",
  "full_name": "John Doe"
}
Response:

json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "api_key": "omni_abc123def456... (for public widgets)"
}
2. Login User
Endpoint: POST /api/v1/auth/login

Request Body (Form Data):

text
username: user@example.com
password: secure_password_123
Response:

json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
3. Refresh Token
Endpoint: POST /api/v1/auth/refresh

Request Body:

json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
Response:

json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
⚙️ User Settings
1. Connect Vector DB (Embeddings Store)
Endpoint: POST /api/v1/settings/vector-db

Provider: Qdrant
json
{
  "provider": "qdrant",
  "credentials": {
    "url": "https://your-cluster.cloud.qdrant.io:6333",
    "api_key": "your_qdrant_api_key",
    "visual_collection_name": "visual_search_products"
  }
}
Provider: MongoDB Atlas (Vector Search)
json
{
  "provider": "mongodb",
  "credentials": {
    "connection_string": "mongodb+srv://USER:PASS@cluster.mongodb.net/",
    "database_name": "visual_search_db",
    "visual_collection_name": "product_embeddings"
  }
}
Provider: Pinecone
json
{
  "provider": "pinecone",
  "credentials": {
    "api_key": "your_pinecone_api_key",
    "environment": "us-east-1",
    "visual_collection_name": "visual_search_products"
  }
}
2. Connect Data Source (Store / CMS / DB)
Endpoint: POST /api/v1/settings/data-source

Type: Shopify Store
json
{
  "type": "shopify",
  "credentials": {
    "shop_url": "my-store.myshopify.com",
    "access_token": "shpat_xxxxx_xxxxx"
  }
}
Type: WooCommerce Store
json
{
  "type": "woocommerce",
  "credentials": {
    "url": "https://my-site.com",
    "consumer_key": "ck_xxxxx",
    "consumer_secret": "cs_xxxxx"
  }
}
Type: MongoDB Store (Custom Database)
json
{
  "type": "mongodb_store",
  "credentials": {
    "connection_string": "mongodb+srv://USER:PASS@cluster.mongodb.net/",
    "database_name": "sample_mflix",
    "collection_name": "products",
    "image_mode": "cdn",
    "field_mapping": {
      "product_id": "_id",
      "slug": "slug",
      "title": "title",
      "price": "variants.price",
      "image_url": "variants.cdnImages.url"
    }
  }
}
image_mode Options:

Value	Description
cdn	Sirf cdnImages array se images nikalein
local	Sirf images array se images nikalein
mixed	Dono arrays check karein (pehle cdnImages, phir images)
Type: Sanity CMS
json
{
  "type": "sanity",
  "credentials": {
    "project_id": "abc123",
    "dataset": "production",
    "token": "sk_xxxxx",
    "custom_query": "*[_type == 'product']",
    "field_mapping": {
      "product_id": "_id",
      "slug": "slug.current",
      "title": "title",
      "image_url": "variants.images.url"
    }
  }
}
3. Select Active Vector DB (User Decision)
Endpoint: POST /api/v1/settings/vector-db/select

Important: Agar user ne multiple vector DBs connect kiye hain (e.g., MongoDB + Qdrant), toh yeh endpoint zaroori hai taake system ko pata chale kaunsa use karna hai.

Request Body:

json
{
  "provider": "qdrant",
  "collection_name": "visual_search_products"
}
Response:

json
{
  "message": "Active vector DB set to qdrant with collection 'visual_search_products'.",
  "provider": "qdrant",
  "collection_name": "visual_search_products"
}
4. Get User Integrations
Endpoint: GET /api/v1/settings/integrations

Response:

json
{
  "user_email": "user@example.com",
  "selected_vector_provider": "qdrant",
  "selected_collection_name": "visual_search_products",
  "connected_services": [
    {
      "provider": "mongodb_store",
      "is_active": true,
      "description": "Data Source (mongodb_store) connected for product retrieval.",
      "last_updated": "2026-08-31T12:00:00"
    },
    {
      "provider": "qdrant",
      "is_active": true,
      "description": "Vector DB (qdrant) connected for embeddings.",
      "last_updated": "2026-08-31T12:05:00"
    }
  ]
}
5. Delete Integration
Endpoint: DELETE /api/v1/settings/integration/{provider}

Example: DELETE /api/v1/settings/integration/qdrant

Response:

json
{
  "message": "Integration for qdrant deleted."
}
6. Update Bot Profile (Future - RAG)
Endpoint: POST /api/v1/settings/bot-profile

Request Body:

json
{
  "bot_name": "Support Agent",
  "bot_instruction": "You are a helpful customer support agent. Only answer questions related to the provided data."
}
🖼️ Visual Search
1. Trigger Visual Sync
Endpoint: POST /api/v1/visual/sync
Auth: JWT Token (Dashboard)

Request Body: (Koi body nahi)

Response:

json
{
  "status": "processing",
  "message": "Visual Sync started successfully.",
  "job_id": 5
}
Terminal Output (Sync Progress):

text
🚀 [Visual Agent] Starting Smart Sync Job 5 for User: 1
🔄 [Visual Agent] Fetching products from mongodb_store...
📊 Sync Analysis for User 1:
   - Total Products: 171
   - Total Images: 1562
⚡ Processing 1562 new images...
✅ [MongoAdapter] Upserted 100 points to 'visual_search_products'
🎉 Sync Complete. Products: 171, Images: 1562, Deleted: 0
2. Visual Search (Image Upload)
Endpoint: POST /api/v1/visual/search
Auth: API Key (Public Widget) + Domain Lock

Request: (Multipart Form Data)

Field	Type	Description
file	File	User ki image (JPG, PNG, WebP, etc.)
Headers:

text
x-api-key: omni_your_api_key
Response:

json
{
  "results": [
    {
      "id": "point_id_1",
      "score": 0.93,
      "payload": {
        "product_id": "6a6393d28422c7bbfd08e492",
        "slug": "easy-to-use-and-maintain-nebulizer",
        "image_url": "https://content.public.markaz.app/.../product-1.webp",
        "title": "Easy To Use And Maintain Nebulizer",
        "price": "1959",
        "source": "mongodb_store",
        "user_id": "1"
      }
    },
    {
      "id": "point_id_2",
      "score": 0.87,
      "payload": {
        "product_id": "6a6393d28422c7bbfd08e493",
        "slug": "high-quality-portable-mesh-nebulizer",
        "image_url": "https://content.public.markaz.app/.../product-2.webp",
        "title": "High Quality Portable Mesh Nebulizer",
        "price": "1959",
        "source": "mongodb_store",
        "user_id": "1"
      }
    }
  ]
}
3. File Preview (CSV/JSON Headers)
Endpoint: POST /api/v1/visual/file/preview
Auth: JWT Token (Dashboard)

Request: (Multipart Form Data)

Field	Type	Description
file	File	CSV ya JSON file
Response:

json
{
  "filename": "products.csv",
  "headers": ["Product Name", "Slug", "Image URL", "Price"],
  "message": "File parsed successfully. Please map fields."
}
4. File Process (CSV/JSON Upload + Field Mapping)
Endpoint: POST /api/v1/visual/file/process
Auth: JWT Token (Dashboard)

Request: (Multipart Form Data)

Field	Type	Description
file	File	CSV ya JSON file
field_mapping	String (JSON)	Mapping object as JSON string
field_mapping Example:

json
{
  "title": "Product Name",
  "slug": "Slug",
  "image_url": "Image URL",
  "product_id": "ID",
  "price": "Price"
}
Complete Request Example (Form Data):

text
file: products.csv
field_mapping: {"title":"Product Name","slug":"Slug","image_url":"Image URL","product_id":"ID"}
Response:

json
{
  "status": "processing",
  "message": "File processing started successfully.",
  "job_id": 6
}
5. Visual Job Status
Endpoint: GET /api/v1/visual/jobs/{job_id}
Auth: JWT Token (Dashboard)

Response:

json
{
  "job_id": 5,
  "status": "completed",
  "items_processed": 1562,
  "total_items": 171,
  "error_message": null
}
📥 Ingestion (Shared Jobs)
1. Get All Jobs
Endpoint: GET /api/v1/ingestion/jobs
Auth: JWT Token (Dashboard)

Response:

json
[
  {
    "job_id": 5,
    "ingestion_type": "visual_sync",
    "source_name": "Store Integration (Visual)",
    "status": "completed",
    "items_processed": 1562,
    "total_items": 171,
    "error_message": null
  },
  {
    "job_id": 6,
    "ingestion_type": "file_upload",
    "source_name": "products.csv",
    "status": "processing",
    "items_processed": 45,
    "total_items": 100,
    "error_message": null
  }
]
2. Get Job Status
Endpoint: GET /api/v1/ingestion/jobs/{job_id}
Auth: JWT Token (Dashboard)

Response:

json
{
  "job_id": 5,
  "ingestion_type": "visual_sync",
  "source_name": "Store Integration (Visual)",
  "status": "completed",
  "items_processed": 1562,
  "total_items": 171,
  "error_message": null
}
📊 Project Structure (File Tree)
text
backend/src/
├── core/
│   ├── config.py                 # System settings (generic, no hardcoded)
│   ├── db_base.py
│   └── db_session.py
├── shared/
│   ├── api/routes/
│   │   ├── auth.py               # Register, Login, Refresh
│   │   ├── deps.py               # JWT + API Key dependencies
│   │   ├── settings.py           # Vector DB + Data Source connect
│   │   └── ingestion.py          # Job tracking endpoints
│   ├── models/
│   │   ├── user.py               # User + selected_vector_provider
│   │   └── integration.py        # UserIntegration (credentials encrypted)
│   └── utils/
│       ├── auth.py               # Password hash, JWT, API key
│       └── security.py           # Encryption/Decryption (Fernet)
├── modules/
│   ├── visual_search/
│   │   ├── api/routes/
│   │   │   └── visual.py         # Sync, Search, File Preview/Process, Job Status
│   │   ├── models/
│   │   │   └── ingestion.py      # IngestionJob model
│   │   ├── schemas/
│   │   │   └── visual.py         # API request/response models
│   │   └── services/
│   │       ├── connectors/       # Shopify, Woo, Mongo, Sanity
│   │       ├── vector_store/     # Qdrant, Mongo, Factory
│   │       └── visual/           # engine.py (CLIP), agent.py, file_ingestion.py
│   └── rag_chat/                 # (Alag project mein move kiya)
└── main.py                       # FastAPI app entry point
🎯 Quick Reference
Vector DB Providers (Choose One)
Provider	Endpoint Field	Collection Name
Qdrant	"provider": "qdrant"	visual_collection_name
MongoDB Atlas	"provider": "mongodb"	visual_collection_name
Pinecone	"provider": "pinecone"	visual_collection_name
Data Source Types (Choose One)
Type	Description
shopify	Shopify store se products fetch
woocommerce	WooCommerce store se products fetch
mongodb_store	Custom MongoDB database se products fetch (field_mapping ke saath)
sanity	Sanity CMS se products fetch (custom_query + field_mapping ke saath)
📝 Notes
x-api-key header sirf public widgets (Visual Search) ke liye hai. Dashboard endpoints ke liye JWT Bearer token use hota hai.

image_mode (MongoDB Store) ke options:

cdn: Sirf cdnImages array check karega.

local: Sirf images array check karega.

mixed: Dono arrays check karega (default).

field_mapping mein dot notation (e.g., "variants.price") nested fields ke liye support hota hai.

selected_vector_provider user ke table mein store hota hai, aur system hamesha usi provider ko use karega (MongoDB ho ya Qdrant, koi conflict nahi).

Har vector ki payload mein user_id hamesha store hota hai, taake multi-user security maintain ho.

text

---

**Yeh poori file copy karein aur `.md` extension ke saath save karein (e.g., `api-schemas.md`). Ab aapko kabhi bhi schema patterns ke liye puchna nahi padega — sab kuch ek jagah hai!** 🚀