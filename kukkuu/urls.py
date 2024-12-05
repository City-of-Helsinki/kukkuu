from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.urls import include, path, re_path
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView
from helusers.admin_site import admin
from rest_framework import routers

from common.utils import get_api_version
from custom_health_checks.views import HealthCheckJSONView
from kukkuu import __version__
from kukkuu.views import SentryGraphQLView
from reports.api import ChildViewSet, EventGroupViewSet, EventViewSet, VenueViewSet

admin.site.index_title = _("Kukkuu backend {api_version}").format(
    api_version=get_api_version()
)

router = routers.DefaultRouter()
router.register(r"children", ChildViewSet)
router.register(r"event", EventViewSet)
router.register(r"event-group", EventGroupViewSet)
router.register(r"venue", VenueViewSet)


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


def readiness(*args, **kwargs):
    response_json = {
        "status": "ok",
        "release": settings.APP_RELEASE,
        "packageVersion": __version__,
        "commitHash": settings.REVISION,
        "buildTime": settings.APP_BUILD_TIME.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
    }
    return JsonResponse(response_json, status=200)


urlpatterns += [
    path(r"healthz", HealthCheckJSONView.as_view(), name="healthz"),
    path("readiness", readiness),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
