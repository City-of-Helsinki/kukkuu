from typing import List, Optional
from unittest import mock

from auditlog.context import set_actor
from auditlog.models import LogEntry
from auditlog.registry import auditlog
from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import RequestFactory, TestCase

from hel_django_auditlog_extra.mixins import AuditlogAdminViewAccessLogMixin
from hel_django_auditlog_extra.tests.models import DummyTestModel

User = get_user_model()

REMOTE_ADDR = "127.0.0.1"


class AuditlogAdminViewAccessLogMixinTest(TestCase):
    def setUp(self):
        # Register the DummyTestModel to audit logging
        auditlog.register(DummyTestModel)

        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword",
            is_staff=True,
            is_superuser=True,
        )
        self.obj1 = DummyTestModel(
            id=1, text_field="text1", number_field=1, boolean_field=True
        )
        self.obj2 = DummyTestModel(
            id=2, text_field="text2", number_field=2, boolean_field=False
        )
        self.all_objects = (self.obj1, self.obj2)
        self.model_admin = self.get_model_admin(result_list=list(self.all_objects))

    def tearDown(self):
        # To fix caching issues when running multiple tests at once...
        ContentType.objects.clear_cache()
        return super().tearDown()

    def get_model_admin(self, result_list: Optional[List] = None, **kwargs):
        class MockedChangeList(ChangeList):
            show_full_result_count = False

            def has_change_permission(self, request, obj=None):
                return True

            def has_delete_permission(self, request, obj=None):
                return True

            def get_queryset(self, request):
                return list(result_list or [])

            def get_results(self, request):
                """
                A mocked get_result is needed to bypass QuerySet functions usage,
                since we are dealing with a static list of unmanaged DummyTestModel
                instances.
                """
                paginator = self.model_admin.get_paginator(
                    request, self.queryset, self.list_per_page
                )
                # Get the number of objects, with admin filters applied.
                result_count = paginator.count
                can_show_all = result_count <= self.list_max_show_all
                multi_page = result_count > self.list_per_page
                self.result_count = result_count
                self.show_full_result_count = self.model_admin.show_full_result_count
                self.show_admin_actions = False
                self.full_result_count = None
                self.can_show_all = can_show_all
                self.multi_page = multi_page
                self.paginator = paginator
                # Mock the result_list of objects.
                self.result_list = self.get_queryset(request)

            def get_object(self, request, object_id, from_field=None):
                return self.obj1

            def get_deleted_objects(self, objs, request):
                return [self.get_object()]

        class DummyTestModelAdmin(AuditlogAdminViewAccessLogMixin, admin.ModelAdmin):
            """
            Register DummyTestModel with DummyTestModelAdmin to test
            Django admin views.
            """

            write_accessed_from_list_view = False

            def get_changelist(self, request, **kwargs):
                return MockedChangeList

        return DummyTestModelAdmin(DummyTestModel, admin.site)

    def assert_access_log(self, log: LogEntry, obj, user=None):
        if not user:
            user = self.user
        self.assertEqual(log.actor, user)
        self.assertEqual(log.remote_addr, REMOTE_ADDR)
        self.assertEqual(log.content_type.model, obj._meta.model_name)
        self.assertEqual(log.object_id, obj.id)

    def test_changelist_view_logging(self):
        for is_write_accessed_enabled in (True, False):
            with self.subTest(write_accessed_from_list_view=is_write_accessed_enabled):
                auditlog_count_on_start = LogEntry.objects.count()
                self.model_admin.write_accessed_from_list_view = (
                    is_write_accessed_enabled
                )
                request = self.factory.get(
                    "/admin/hel_django_auditlog_extra/dummytestmodel/"
                )
                request.user = self.user
                with set_actor(request.user, remote_addr=REMOTE_ADDR):
                    response = self.model_admin.changelist_view(request)
                    self.assertEqual(response.status_code, 200)
                    if is_write_accessed_enabled:
                        self.assertEqual(
                            LogEntry.objects.count(),
                            auditlog_count_on_start + len(self.all_objects),
                        )
                    else:
                        self.assertEqual(
                            LogEntry.objects.count(), auditlog_count_on_start
                        )
                    log = LogEntry.objects.first()
                    self.assertEqual(log.actor, self.user)
                    self.assertEqual(log.remote_addr, REMOTE_ADDR)
                    self.assertEqual(
                        log.content_type.model, DummyTestModel._meta.model_name
                    )

    def test_change_view(self):
        request = self.factory.get(
            f"/admin/hel_django_auditlog_extra/dummytestmodel/{self.obj1.pk}/change/"
        )
        request.user = self.user
        auditlog_count_on_start = LogEntry.objects.count()
        with set_actor(request.user, remote_addr=REMOTE_ADDR):
            with mock.patch.object(
                self.model_admin,
                "get_object",
                return_value=self.obj1,
            ):
                response = self.model_admin.change_view(request, str(self.obj1.pk))
                self.assertEqual(response.status_code, 200)
                self.assertEqual(LogEntry.objects.count(), auditlog_count_on_start + 1)

                log = LogEntry.objects.first()
                self.assert_access_log(log, self.obj1)

    def test_history_view(self):
        request = self.factory.get(
            f"/admin/hel_django_auditlog_extra/dummytestmodel/{self.obj1.pk}/history/"
        )
        request.user = self.user
        auditlog_count_on_start = LogEntry.objects.count()
        with set_actor(request.user, remote_addr=REMOTE_ADDR):
            with mock.patch.object(
                self.model_admin,
                "get_object",
                return_value=self.obj1,
            ):
                response = self.model_admin.history_view(request, str(self.obj1.pk))
                self.assertEqual(response.status_code, 200)
                self.assertEqual(LogEntry.objects.count(), auditlog_count_on_start + 1)

                log = LogEntry.objects.first()
                self.assert_access_log(log, self.obj1)

    def test_delete_view(self):
        request = self.factory.get(
            f"/admin/hel_django_auditlog_extra/dummytestmodel/{self.obj1.pk}/delete/"
        )
        request.user = self.user
        auditlog_count_on_start = LogEntry.objects.count()
        with set_actor(request.user, remote_addr=REMOTE_ADDR):
            with mock.patch.object(
                self.model_admin,
                "get_object",
                return_value=self.obj1,
            ):
                response = self.model_admin.delete_view(request, str(self.obj1.pk))
                self.assertEqual(response.status_code, 200)
                self.assertEqual(LogEntry.objects.count(), auditlog_count_on_start + 1)
                log = LogEntry.objects.first()
                self.assert_access_log(log, self.obj1)
