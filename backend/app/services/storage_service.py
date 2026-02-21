import os
import aiofiles
from typing import Any, BinaryIO
from backend.app.config import settings

class StorageService:
    def __init__(self):
        self.backend = settings.STORAGE_BACKEND
        
        # Local Setup
        if self.backend == "local":
            self.upload_dir = os.path.join(os.getcwd(), "uploads")
            os.makedirs(self.upload_dir, exist_ok=True)
            
    async def upload(self, file_content: bytes, filename: str, org_id: str) -> str:
        """Uploads file to the chosen storage backend and returns the key/url."""
        key = f"{org_id}/{filename}"
        
        if self.backend == "local":
            org_dir = os.path.join(self.upload_dir, org_id)
            os.makedirs(org_dir, exist_ok=True)
            filepath = os.path.join(org_dir, filename)
            async with aiofiles.open(filepath, 'wb') as f:
                await f.write(file_content)
            return f"local://{key}"
            
        elif self.backend == "supabase":
            # Stub for Supabase Storage Phase implementation
            pass
            
        elif self.backend == "r2":
            # Stub for Cloudflare R2 Phase implementation
            pass
            
        raise ValueError(f"Unknown storage backend: {self.backend}")

    async def download(self, key: str) -> bytes:
        if self.backend == "local":
            filepath = os.path.join(self.upload_dir, key.replace("local://", ""))
            async with aiofiles.open(filepath, 'rb') as f:
                return await f.read()
        return b""

storage_service = StorageService()
