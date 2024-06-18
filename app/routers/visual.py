from fastapi import APIRouter, Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy.orm import Session

from .. import models
from ..config.metadata_tag import MetadataTag
from ..utils.dependency import Dependency

api_router = APIRouter(
    prefix=MetadataTag.__tag_visual__.prefix, tags=[MetadataTag.__tag_visual__.name]
)


@api_router.get("/mail_template", response_class=HTMLResponse)
async def view_mail_template(
    request: Request, db: Session = Depends(Dependency.get_db)
):
    templates = Jinja2Templates(directory="app/templates")
    name = "mail.html"
    alert_queue = db.query(models.alert_queue.AlertQueue).all()
    context = {"alert_queue": alert_queue, "SUBJECT": "DEMO", "app_uri": ".."}
    return templates.TemplateResponse(request=request, name=name, context=context)
