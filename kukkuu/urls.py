from csp.decorators import csp_update
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
from kukkuu.consts import CSP
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

IS_GRAPHIQL_ENABLED = settings.ENABLE_GRAPHIQL or settings.DEBUG


# Add unsafe-inline to enable GraphiQL interface at /graphql/
@csp_update(
    SCRIPT_SRC=settings.CSP_SCRIPT_SRC
    + ([CSP.UNSAFE_INLINE] if IS_GRAPHIQL_ENABLED else [])
)
@csrf_exempt
def graphql_view(request, *args, **kwargs):
    return SentryGraphQLView.as_view(graphiql=IS_GRAPHIQL_ENABLED)(
        request, *args, **kwargs
    )


# URL patterns required for Django admin Keycloak login:
# (See https://github.com/City-of-Helsinki/django-helusers/blob/v0.13.0/README.md)
URL_PATTERNS_FOR_DJANGO_ADMIN_KEYCLOAK_LOGIN = [
    path("pysocial/", include("social_django.urls", namespace="social")),
    path("helauth/", include("helusers.urls")),
]

urlpatterns = [
    *URL_PATTERNS_FOR_DJANGO_ADMIN_KEYCLOAK_LOGIN,
    path("admin/", admin.site.urls),
    re_path(r"^graphql/?$", graphql_view),
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
