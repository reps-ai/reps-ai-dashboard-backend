from fastapi import APIRouter, Path, Body, File, UploadFile
from app.schemas.leads.import_schemas import ImportRequest, ImportResponse, ImportJobStatus

router = APIRouter(prefix="/import")

@router.post("", response_model=ImportResponse)
async def import_leads(
    file: UploadFile = File(...),
    mapping: ImportRequest = Body(...)
):
    """
    Import leads from a file.
    """
    # Implementation will be added later
    pass

@router.get("/{job_id}", response_model=ImportJobStatus)
async def get_import_status(
    job_id: str = Path(..., description="The ID of the import job to check")
):
    """
    Get the status of a lead import job.
    """
    # Implementation will be added later
    pass 