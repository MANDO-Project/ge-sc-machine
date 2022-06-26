import io
from functools import lru_cache

import yaml
from logbook import Logger
from fastapi.responses import Response
from fastapi_rfc7807 import middleware
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.staticfiles import StaticFiles

from .api.common import app
from .api.views import line_level_bug
from .api.views import contract_level_bug
from .config import settings


logger = Logger(__name__)
middleware.register(app)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="/static/redoc.standalone.js",
    )


app.include_router(line_level_bug.router, prefix=settings.PREFIX)
app.include_router(contract_level_bug.router, prefix=settings.PREFIX)


# Additional yaml version of openapi.json
# Ref: https://github.com/tiangolo/fastapi/issues/1140#issuecomment-659469034
@app.get('/openapi.yaml', include_in_schema=False)
@lru_cache()
def read_openapi_yaml() -> Response:
    openapi_json = app.openapi()
    yaml_s = io.StringIO()
    yaml.dump(openapi_json, yaml_s)
    return Response(yaml_s.getvalue(), media_type='text/yaml')
