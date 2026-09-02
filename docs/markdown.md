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