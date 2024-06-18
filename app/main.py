from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config.env import settings
from .config.lifespan import lifespan
from .config.metadata_tag import MetadataTag
from .utils.middleware import add_middlewares

# CREATE APP WITH GENERIC PARAMS
app = FastAPI(
    # define the tags and their order in documentation
    openapi_tags=MetadataTag.tag_list(),
    # don't use the generated documentation urls
    docs_url=None,
    redoc_url=None,
    # use the env ROOT_PATH to define the root url
    root_path=settings.root_path,
    lifespan=lifespan,
    title=settings.fastapi_title,
    version=settings.app_version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
add_middlewares(app)
