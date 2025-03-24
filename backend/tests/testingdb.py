from fastapi import Depends
from db.connections.database import get_db
from db.helpers.lead import get_lead_with_related_data


get_lead_with_related_data(Depends(get_db),"123454333")


