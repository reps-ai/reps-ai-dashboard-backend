from fastapi import APIRouter, Depends
from app.dependencies import get_current_user, get_admin_user

router = APIRouter()

@router.get("/prompts")
async def get_prompts(current_user = Depends(get_current_user)):
    """
    Get all available AI agent prompts.
    """
    # TODO: Implement prompts retrieval logic
    return {"message": "Get prompts endpoint"}

@router.get("/prompts/{prompt_id}")
async def get_prompt(prompt_id: str, current_user = Depends(get_current_user)):
    """
    Get a specific AI agent prompt.
    """
    # TODO: Implement prompt retrieval logic
    return {"message": f"Get prompt {prompt_id} endpoint"}

@router.post("/prompts")
async def create_prompt(current_user = Depends(get_admin_user)):
    """
    Create a new AI agent prompt.
    """
    # TODO: Implement prompt creation logic
    return {"message": "Create prompt endpoint"}

@router.put("/prompts/{prompt_id}")
async def update_prompt(prompt_id: str, current_user = Depends(get_admin_user)):
    """
    Update an existing AI agent prompt.
    """
    # TODO: Implement prompt update logic
    return {"message": f"Update prompt {prompt_id} endpoint"}

@router.delete("/prompts/{prompt_id}")
async def delete_prompt(prompt_id: str, current_user = Depends(get_admin_user)):
    """
    Delete an AI agent prompt.
    """
    # TODO: Implement prompt deletion logic
    return {"message": f"Delete prompt {prompt_id} endpoint"} 