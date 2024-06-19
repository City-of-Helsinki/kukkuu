from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.urls import include, path, re_path
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView
from helusers.admin_site import admin
from rest_framework import routers

from common.utils import get_api_version
from kukkuu.views import SentryGraphQLView
from reports.api import ChildViewSet

admin.site.index_title = _("Kukkuu backend {api_version}").format(
    api_version=get_api_version()
)

router = routers.DefaultRouter()
router.register(r"children", ChildViewSet)


urlpatterns = [
    path("admin/", admin.site.urls),
    re_path(
        r"^graphql/?$",
        csrf_exempt(
            SentryGraphQLView.as_view(
                graphiql=settings.ENABLE_GRAPHIQL or settings.DEBUG
            )
        ),
    ),
    path("reports/", include(router.urls)),
    path("reports/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "reports/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    path("gdpr-api/", include("helsinki_gdpr.urls")),
]


#
# Kubernetes liveness & readiness probes
#
def healthz(*args, **kwargs):
    return HttpResponse(status=200)


def readiness(*args, **kwargs):
    return HttpResponse(status=200)


urlpatterns += [path("healthz", healthz), path("readiness", readiness)]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
