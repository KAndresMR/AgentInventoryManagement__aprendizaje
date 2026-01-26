import strawberry
from api.graphql.queries import Query

schema = strawberry.Schema(query=Query)
