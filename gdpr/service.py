import logging
from typing import TYPE_CHECKING, Optional

from helsinki_gdpr.types import ErrorResponse

from subscriptions.models import FreeSpotNotificationSubscription

if TYPE_CHECKING:
    from users.models import User as UserType

logger = logging.getLogger(__name__)


def get_user(user: "UserType") -> "UserType":
    """Function used by the Helsinki Profile GDPR API to get the "user"
    instance from the "GDPR Model"
    instance. Since in our case the GDPR Model
    and the user are one and the same, we simply return
    the same User instance that is given as a parameter.

    Args:
        user (UserType): the User instance whose GDPR data is being queried

    Returns:
        UserType: the same User instance

    References:
        https://github.com/City-of-Helsinki/helsinki-profile-gdpr-api/blob/808dcd30a745f6d18cdf36ccaf07b0cd25844ab0/README.md.
        https://github.com/City-of-Helsinki/kerrokantasi/blob/256134d4049f0bd1598d59caaebbb813be2d7d9c/kerrokantasi/gdpr.py.
    """
    logger.info(f"GDPR data request called for user '{user.uuid}'.")
    return user


def clear_data(user: "UserType", dry_run: bool) -> Optional[ErrorResponse]:
    """Function used by the Helsinki Profile GDPR API to clear GDPR data fields
    related to the user. The User instance or
    any related model instances won't be deleted,
    but the user will be disabled and the user data and
    the related data will be anonymised.
    The GDPR API package will run this within a transaction.

    Args:
        user (UserType): the User instance to be deleted along with related GDPR data
        dry_run (bool): a boolean telling if this is a dry run of the function or not

    Returns:
        Optional[ErrorResponse]: any errors that occured,
            e.g. the object might not exist or the data deletion might be denied.

    References:
        https://github.com/City-of-Helsinki/helsinki-profile-gdpr-api/blob/808dcd30a745f6d18cdf36ccaf07b0cd25844ab0/README.md.
        https://github.com/City-of-Helsinki/kerrokantasi/blob/256134d4049f0bd1598d59caaebbb813be2d7d9c/kerrokantasi/gdpr.py.
    """
    from users.models import Guardian

    logger.info(f"GDPR data clear called for user '{user.uuid}'.")
    user.clear_gdpr_sensitive_data_fields()
    try:
        user.guardian.clear_gdpr_sensitive_data_fields()
        for child in user.guardian.children.all():
            child.clear_gdpr_sensitive_data_fields()
            FreeSpotNotificationSubscription.objects.filter(child=child).delete()

    except Guardian.DoesNotExist:
        logger.warning(
            "Could not call 'clear_gdpr_sensitive_data_fields' for a guardian object, "
            f"since there is no guardian linked to the user {user.uuid}."
        )
