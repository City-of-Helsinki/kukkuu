import pytest
from django.apps import apps

from common.tests.conftest import *  # noqa
from tags.models import Tag

TAG_MODELS = [model for model in apps.get_models() if issubclass(model, Tag)]


@pytest.fixture(params=TAG_MODELS, ids=lambda model: model._meta.model_name)
def tag_model(request):
    return request.param
