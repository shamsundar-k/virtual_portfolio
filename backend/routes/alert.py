from fastapi import APIRouter
from models.alert import Alert, AlertCreate
from services.alert_service import list_alerts, create_alert, delete_alert

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=list[Alert])
async def get_alerts():
    return await list_alerts()


@router.post("", response_model=Alert, status_code=201)
async def create(data: AlertCreate):
    return await create_alert(data)


@router.delete("/{alert_id}", status_code=204)
async def delete(alert_id: str):
    await delete_alert(alert_id)
