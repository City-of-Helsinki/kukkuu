from common.utils import get_node_id_from_global_id
from kukkuu.exceptions import ObjectDoesNotExistError
from tags.models import ThemePath


class ChildAPIService:
    """
    Service class for Child GraphQL API business logic.
    """

    class Resolver:
        """
        Resolves Relay Global IDs into model instances.
        """

        @staticmethod
        def theme_path(info, theme_path_global_id: str | None) -> ThemePath | None:
            if not theme_path_global_id:
                return None
            try:
                theme_path_id = get_node_id_from_global_id(
                    theme_path_global_id, "ThemePathNode"
                )
            except ValueError:
                theme_path_id = None
            if theme_path_id:
                try:
                    return ThemePath.objects.get(pk=theme_path_id)
                except ThemePath.DoesNotExist:
                    pass
            raise ObjectDoesNotExistError(
                f"ThemePath with ID {theme_path_global_id} does not exist."
            )

    class Cleaner:
        """
        Normalizes and cleans GraphQL mutation input kwargs for Child models.
        """

        @classmethod
        def theme_path_id(cls, info, kwargs: dict) -> None:
            if "theme_path_id" not in kwargs:
                return
            theme_path_global_id = kwargs.pop("theme_path_id")
            kwargs["theme_path"] = ChildAPIService.Resolver.theme_path(
                info, theme_path_global_id
            )
