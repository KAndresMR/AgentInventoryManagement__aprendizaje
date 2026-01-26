from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from api.graphql.schema import schema
from config.settings import settings

app = FastAPI(title=settings.app_name)

graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

@app.get("/health")
def health_check():
    return {"status": "ok"}
