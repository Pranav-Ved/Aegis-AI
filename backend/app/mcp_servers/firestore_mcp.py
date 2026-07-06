import structlog
from typing import Optional, List, Dict, Any

from app.mcp_servers.base import BaseMCPServer
from app.core.database import get_db

logger = structlog.get_logger(__name__)

class FirestoreMCPServer(BaseMCPServer):
    name = "firestore-mcp"
    description = "Provides read, write, query, and batch operations for firestore collections"

    @property
    def db_mode(self) -> str:
        db = get_db()
        from app.core.database import MockDB
        return "mock" if isinstance(db, MockDB) else "firestore"

    async def create_document(self, collection: str, data: dict, doc_id: Optional[str] = None) -> dict:
        """Create a new document inside a collection."""
        async def _run():
            db = get_db()
            new_id = await db.create_document(collection, data, doc_id)
            return {"doc_id": new_id, "collection": collection, "success": True}
        res = await self._execute_tool("create_document", _run)
        return res.to_dict()

    async def get_document(self, collection: str, doc_id: str) -> dict:
        """Retrieve a single document from a collection by ID."""
        async def _run():
            db = get_db()
            doc_data = await db.get_document(collection, doc_id)
            return doc_data
        res = await self._execute_tool("get_document", _run)
        return res.to_dict()

    async def update_document(self, collection: str, doc_id: str, data: dict) -> dict:
        """Update fields inside a document. Supports dot-notation for nested fields."""
        async def _run():
            db = get_db()
            success = await db.update_document(collection, doc_id, data)
            return {"success": success}
        res = await self._execute_tool("update_document", _run)
        return res.to_dict()

    async def delete_document(self, collection: str, doc_id: str) -> dict:
        """Delete a document from a collection by ID."""
        async def _run():
            db = get_db()
            success = await db.delete_document(collection, doc_id)
            return {"success": success}
        res = await self._execute_tool("delete_document", _run)
        return res.to_dict()

    async def query_collection(
        self, 
        collection: str, 
        filters: List[dict] = None, 
        limit: int = 100, 
        order_by: str = None
    ) -> dict:
        """Query a collection with filters, limits, and sort orders."""
        async def _run():
            db = get_db()
            results = await db.query_collection(collection, filters=filters, limit=limit, order_by=order_by)
            return results
        res = await self._execute_tool("query_collection", _run)
        return res.to_dict()

    async def batch_write(self, operations: List[dict]) -> dict:
        """Execute multiple database operations in a single atomic transaction transaction."""
        async def _run():
            db = get_db()
            success = await db.batch_write(operations)
            return {"success": success}
        res = await self._execute_tool("batch_write", _run)
        return res.to_dict()

firestore_mcp = FirestoreMCPServer()
