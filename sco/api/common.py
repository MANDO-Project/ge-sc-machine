from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title='MANDO-Vulnerability-Detection', redoc_url='/api-doc', docs_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
