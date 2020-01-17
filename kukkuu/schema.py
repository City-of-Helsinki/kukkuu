import graphene

import children.schema
import events.schema
import users.schema
import venues.schema


class Mutation(
    children.schema.Mutation,
    users.schema.Mutation,
    events.schema.Mutation,
    venues.schema.Mutation,
    graphene.ObjectType,
):
    pass


class Query(
    children.schema.Query,
    users.schema.Query,
    events.schema.Query,
    venues.schema.Query,
    graphene.ObjectType,
):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
