from fastapi import APIRouter

from models.journal import JournalCreate, JournalEntry
from services.journal_service import create_entry, delete_entry, list_entries

router = APIRouter(prefix="/journal", tags=["journal"])


@router.get("", response_model=list[JournalEntry])
async def get_entries():
    return await list_entries()


@router.post("", response_model=JournalEntry, status_code=201)
async def create(data: JournalCreate):
    return await create_entry(data)


@router.delete("/{entry_id}", status_code=204)
async def delete(entry_id: str):
    await delete_entry(entry_id)
