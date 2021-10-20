import graphene

import children.schema
import events.schema
import languages.schema
import messaging.schema
import projects.schema
import subscriptions.schema
import users.schema
import venues.schema
from events.schema import (
    InternalEventTicketSystem,
    InternalOccurrenceTicketSystem,
    TicketmasterEventTicketSystem,
    TicketmasterOccurrenceTicketSystem,
)


class Mutation(
    children.schema.Mutation,
    users.schema.Mutation,
    events.schema.Mutation,
    venues.schema.Mutation,
    subscriptions.schema.Mutation,
    messaging.schema.Mutation,
    graphene.ObjectType,
):
    pass


class Query(
    children.schema.Query,
    users.schema.Query,
    projects.schema.Query,
    events.schema.Query,
    venues.schema.Query,
    languages.schema.Query,
    messaging.schema.Query,
    graphene.ObjectType,
):
    pass


schema = graphene.Schema(
    query=Query,
    mutation=Mutation,
    types=[
        TicketmasterEventTicketSystem,
        InternalEventTicketSystem,
        TicketmasterOccurrenceTicketSystem,
        InternalOccurrenceTicketSystem,
    ],
)
