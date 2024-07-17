# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots[
    "test_create_non_existing_and_update_existing_notifications 1"
] = """event_published|event_published fi updated subject|event_published en updated subject|event_published sv updated subject|event_published fi updated body_text|event_published en updated body_text|event_published sv updated body_text|||
occurrence_enrolment|occurrence_enrolment fi updated subject|occurrence_enrolment en updated subject|occurrence_enrolment sv updated subject|occurrence_enrolment fi updated body_text|occurrence_enrolment en updated body_text|occurrence_enrolment sv updated body_text|||"""

snapshots[
    "test_create_non_existing_notifications 1"
] = """event_published|event_published fi original subject|event_published en original subject|event_published sv original subject|event_published fi original body_text|event_published en original body_text|event_published sv original body_text|||
occurrence_enrolment|occurrence_enrolment fi updated subject|occurrence_enrolment en updated subject|occurrence_enrolment sv updated subject|occurrence_enrolment fi updated body_text|occurrence_enrolment en updated body_text|occurrence_enrolment sv updated body_text|||"""

snapshots["test_update_notifications 1"] = (
    "event_published|event_published fi updated subject|event_published en updated subject|event_published sv updated subject|event_published fi updated body_text|event_published en updated body_text|event_published sv updated body_text|||"
)
