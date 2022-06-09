import io
from functools import lru_cache

import yaml
from logbook import Logger
from fastapi.responses import Response
from fastapi_rfc7807 import middleware

from .api.common import app
from .api.views import line_level_bug
from .config import settings_access_contro


logger = Logger(__name__)
middleware.register(app)
app.include_router(line_level_bug.router, prefix=settings_access_contro.PREFIX)


# Additional yaml version of openapi.json
# Ref: https://github.com/tiangolo/fastapi/issues/1140#issuecomment-659469034
@app.get('/openapi.yaml', include_in_schema=False)
@lru_cache()
def read_openapi_yaml() -> Response:
    openapi_json = app.openapi()
    yaml_s = io.StringIO()
    yaml.dump(openapi_json, yaml_s)
    return Response(yaml_s.getvalue(), media_type='text/yaml')
