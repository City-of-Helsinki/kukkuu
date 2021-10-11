import factory

from children.factories import ChildFactory
from events.factories import OccurrenceFactory
from subscriptions.models import FreeSpotNotificationSubscription


class FreeSpotNotificationSubscriptionFactory(factory.django.DjangoModelFactory):
    occurrence = factory.SubFactory(OccurrenceFactory)
    child = factory.SubFactory(ChildFactory)

    class Meta:
        model = FreeSpotNotificationSubscription
