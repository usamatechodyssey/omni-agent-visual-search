import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from typing import Dict, List, Any, Optional

# Internal Imports
from backend.src.shared.db.session import get_db
from backend.src.shared.models.user import User
from backend.src.shared.models.integration import UserIntegration
from backend.src.shared.api.routes.deps import get_current_user

# Connectors
from backend.src.modules.visual_search.services.connectors.shopify_connector import ShopifyConnector
from backend.src.modules.visual_search.services.connectors.woocommerce_connector import WooCommerceConnector
from backend.src.modules.visual_search.services.connectors.mongo_connector import MongoProductConnector
from backend.src.modules.visual_search.services.connectors.sanity_connector import SanityConnector

router = APIRouter()

# ==========================================
# DATA MODELS
# ==========================================
class VectorDBUpdateRequest(BaseModel):
    provider: str
    credentials: Dict[str, Any]

class DataSourceUpdateRequest(BaseModel):
    type: str
    credentials: Dict[str, Any]

class SelectVectorDBRequest(BaseModel):
    provider: str
    collection_name: str

class ConnectedServiceResponse(BaseModel):
    provider: str
    is_active: bool
    description: Optional[str] = None
    last_updated: Optional[str] = None

class UserSettingsResponse(BaseModel):
    user_email: str
    # 🔥 NEW FIELD ADDED
    api_key: str
    selected_vector_provider: str
    selected_collection_name: str
    connected_services: List[ConnectedServiceResponse]

# ==========================================
# VALIDATION HELPERS
# ==========================================
def validate_vector_db_credentials(provider: str, credentials: Dict[str, Any]) -> bool:
    if provider == "qdrant":
        return bool(credentials.get("url") and credentials.get("api_key"))
    elif provider == "mongodb":
        return bool(credentials.get("connection_string"))
    elif provider == "pinecone":
        return bool(credentials.get("api_key") and credentials.get("environment"))
    return False

def validate_data_source_credentials(type: str, credentials: Dict[str, Any]) -> bool:
    if type == "shopify":
        return bool(credentials.get("shop_url") and credentials.get("access_token"))
    elif type == "woocommerce":
        return bool(credentials.get("url") and credentials.get("consumer_key") and credentials.get("consumer_secret"))
    elif type == "mongodb_store":
        return bool(credentials.get("connection_string") and credentials.get("collection_name"))
    elif type == "sanity":
        return bool(credentials.get("project_id") and credentials.get("dataset") and credentials.get("token"))
    return False

# ==========================================
# 1. CONNECT VECTOR DB
# ==========================================
@router.post("/settings/vector-db", status_code=status.HTTP_201_CREATED)
async def connect_vector_db(
    data: VectorDBUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        if not validate_vector_db_credentials(data.provider, data.credentials):
            raise HTTPException(status_code=400, detail="Invalid Vector DB credentials.")

        credentials_json = json.dumps(data.credentials)
        description = f"Vector DB ({data.provider}) connected for embeddings."

        query = select(UserIntegration).where(
            UserIntegration.user_id == str(current_user.id),
            UserIntegration.provider == data.provider
        )
        result = await db.execute(query)
        existing_integration = result.scalars().first()

        if existing_integration:
            existing_integration.credentials = credentials_json
            existing_integration.is_active = True
            existing_integration.profile_description = description
        else:
            new_integration = UserIntegration(
                user_id=str(current_user.id),
                provider=data.provider,
                is_active=True,
                credentials=credentials_json,
                profile_description=description
            )
            db.add(new_integration)

        await db.commit()
        return {"message": f"Vector DB ({data.provider}) connected.", "provider": data.provider}

    except HTTPException as he:
        raise he
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# 2. CONNECT DATA SOURCE
# ==========================================
@router.post("/settings/data-source", status_code=status.HTTP_201_CREATED)
async def connect_data_source(
    data: DataSourceUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        if not validate_data_source_credentials(data.type, data.credentials):
            raise HTTPException(status_code=400, detail="Invalid Data Source credentials.")

        success, message = test_data_source_connection(data.type, data.credentials)
        if not success:
            raise HTTPException(status_code=400, detail=message)

        provider = data.type
        credentials_json = json.dumps(data.credentials)
        description = f"Data Source ({data.type}) connected for product retrieval."

        query = select(UserIntegration).where(
            UserIntegration.user_id == str(current_user.id),
            UserIntegration.provider == provider
        )
        result = await db.execute(query)
        existing_integration = result.scalars().first()

        if existing_integration:
            existing_integration.credentials = credentials_json
            existing_integration.is_active = True
            existing_integration.profile_description = description
        else:
            new_integration = UserIntegration(
                user_id=str(current_user.id),
                provider=provider,
                is_active=True,
                credentials=credentials_json,
                profile_description=description
            )
            db.add(new_integration)

        await db.commit()
        return {"message": f"Data Source ({data.type}) connected.", "provider": data.type}

    except HTTPException as he:
        raise he
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# 3. SELECT ACTIVE VECTOR DB (User Decision) 🔥
# ==========================================
@router.post("/settings/vector-db/select")
async def select_active_vector_db(
    data: SelectVectorDBRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        query = select(UserIntegration).where(
            UserIntegration.user_id == str(current_user.id),
            UserIntegration.provider == data.provider,
            UserIntegration.is_active == True
        )
        result = await db.execute(query)
        integration = result.scalars().first()

        if not integration:
            raise HTTPException(status_code=400, detail=f"{data.provider} is not connected.")

        current_user.selected_vector_provider = data.provider
        current_user.selected_collection_name = data.collection_name
        db.add(current_user)
        await db.commit()

        return {
            "message": f"Active vector DB set to {data.provider} with collection '{data.collection_name}'.",
            "provider": data.provider,
            "collection_name": data.collection_name
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# 4. GET USER INTEGRATIONS
# ==========================================
@router.get("/settings/integrations", response_model=UserSettingsResponse)
async def get_user_integrations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(UserIntegration).where(UserIntegration.user_id == str(current_user.id))
    result = await db.execute(query)
    integrations = result.scalars().all()

    connected_services = [
        ConnectedServiceResponse(
            provider=i.provider,
            is_active=i.is_active,
            description=i.profile_description,
            last_updated=str(i.updated_at) if i.updated_at else str(i.created_at)
        )
        for i in integrations
    ]

    return {
        "user_email": current_user.email,
        # 🔥 YAHAN API KEY RETURN HO RAHI HAI
        "api_key": current_user.api_key or "",
        "selected_vector_provider": current_user.selected_vector_provider or "",
        "selected_collection_name": current_user.selected_collection_name or "",
        "connected_services": connected_services
    }

# ==========================================
# 5. DELETE INTEGRATION
# ==========================================
@router.delete("/settings/integration/{provider}", status_code=status.HTTP_200_OK)
async def delete_integration(
    provider: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        query = select(UserIntegration).where(
            UserIntegration.user_id == str(current_user.id),
            UserIntegration.provider == provider
        )
        result = await db.execute(query)
        integration = result.scalars().first()

        if not integration:
            raise HTTPException(status_code=404, detail="Integration not found.")

        await db.delete(integration)
        await db.commit()
        return {"message": f"Integration for {provider} deleted."}

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# HELPER: CONNECTOR INSTANCE & TEST
# ==========================================
def get_connector_instance(type: str, credentials: Dict[str, Any]):
    if type == "shopify":
        return ShopifyConnector(credentials)
    elif type == "woocommerce":
        return WooCommerceConnector(credentials)
    elif type == "mongodb_store":
        return MongoProductConnector(credentials)
    elif type == "sanity":
        return SanityConnector(credentials)
    return None

def test_data_source_connection(type: str, credentials: Dict[str, Any]) -> tuple[bool, str]:
    try:
        connector = get_connector_instance(type, credentials)
        if connector and hasattr(connector, "connect"):
            success = connector.connect()
            if success:
                return True, "Connection successful."
            else:
                return False, "Connection failed. Check credentials."
        return True, "Skipped connection test."
    except Exception as e:
        return False, f"Connection error: {str(e)}"