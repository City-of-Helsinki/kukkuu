# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_cannot_send_message_again_without_force 1"] = [
    "kukkuu@example.com|['johndoe@example.com']|Otsikko|Ruumisteksti."
]

snapshots["test_message_sending[en] 1"] = [
    "kukkuu@example.com|['johndoe@example.com']|Subject|Body text."
]

snapshots["test_message_sending[fi] 1"] = [
    "kukkuu@example.com|['johndoe@example.com']|Otsikko|Ruumisteksti."
]

snapshots["test_message_sending_with_filters[event-all] 1"] = [
    ["attended-another-event@example.com"],
    ["attended-occurrence-yesterday-1@example.com"],
    ["attended-occurrence-yesterday-2@example.com"],
    ["enrolled-another-event@example.com"],
    ["enrolled-both-events@example.com"],
    ["enrolled-occurrence-tomorrow-1@example.com"],
    ["enrolled-occurrence-tomorrow-2@example.com"],
    ["subscribed-another-event@example.com"],
    ["subscribed-occurrence-tomorrow-1@example.com"],
    ["subscribed-occurrence-tomorrow-2@example.com"],
]

snapshots["test_message_sending_with_filters[event-attended] 1"] = [
    ["attended-occurrence-yesterday-1@example.com"],
    ["attended-occurrence-yesterday-2@example.com"],
]

snapshots["test_message_sending_with_filters[event-enrolled] 1"] = [
    ["enrolled-both-events@example.com"],
    ["enrolled-occurrence-tomorrow-1@example.com"],
    ["enrolled-occurrence-tomorrow-2@example.com"],
]

snapshots["test_message_sending_with_filters[event-invited] 1"] = [
    ["attended-another-event@example.com"],
    ["attended-occurrence-yesterday-1@example.com"],
    ["attended-occurrence-yesterday-2@example.com"],
    ["enrolled-another-event@example.com"],
    ["enrolled-occurrence-tomorrow-1@example.com"],
    ["enrolled-occurrence-tomorrow-2@example.com"],
    ["subscribed-another-event@example.com"],
    ["subscribed-occurrence-tomorrow-1@example.com"],
    ["subscribed-occurrence-tomorrow-2@example.com"],
]

snapshots[
    "test_message_sending_with_filters[event-subscribed_to_free_spot_notification] 1"
] = [
    ["subscribed-occurrence-tomorrow-1@example.com"],
    ["subscribed-occurrence-tomorrow-2@example.com"],
]

snapshots["test_message_sending_with_filters[no_event_or_occurrence-all] 1"] = [
    ["attended-another-event@example.com"],
    ["attended-occurrence-yesterday-1@example.com"],
    ["attended-occurrence-yesterday-2@example.com"],
    ["enrolled-another-event@example.com"],
    ["enrolled-both-events@example.com"],
    ["enrolled-occurrence-tomorrow-1@example.com"],
    ["enrolled-occurrence-tomorrow-2@example.com"],
    ["subscribed-another-event@example.com"],
    ["subscribed-occurrence-tomorrow-1@example.com"],
    ["subscribed-occurrence-tomorrow-2@example.com"],
]

snapshots["test_message_sending_with_filters[no_event_or_occurrence-attended] 1"] = [
    ["attended-another-event@example.com"],
    ["attended-occurrence-yesterday-1@example.com"],
    ["attended-occurrence-yesterday-2@example.com"],
]

snapshots["test_message_sending_with_filters[no_event_or_occurrence-enrolled] 1"] = [
    ["enrolled-another-event@example.com"],
    ["enrolled-both-events@example.com"],
    ["enrolled-occurrence-tomorrow-1@example.com"],
    ["enrolled-occurrence-tomorrow-2@example.com"],
]

snapshots["test_message_sending_with_filters[no_event_or_occurrence-invited] 1"] = [
    ["attended-another-event@example.com"],
    ["attended-occurrence-yesterday-1@example.com"],
    ["attended-occurrence-yesterday-2@example.com"],
    ["enrolled-another-event@example.com"],
    ["enrolled-occurrence-tomorrow-1@example.com"],
    ["enrolled-occurrence-tomorrow-2@example.com"],
    ["subscribed-another-event@example.com"],
    ["subscribed-occurrence-tomorrow-1@example.com"],
    ["subscribed-occurrence-tomorrow-2@example.com"],
]

snapshots[
    "test_message_sending_with_filters[no_event_or_occurrence-subscribed_to_free_spot_notification] 1"
] = [
    ["subscribed-another-event@example.com"],
    ["subscribed-occurrence-tomorrow-1@example.com"],
    ["subscribed-occurrence-tomorrow-2@example.com"],
]

snapshots["test_message_sending_with_filters[occurrence_tomorrow_1-all] 1"] = [
    ["attended-another-event@example.com"],
    ["attended-occurrence-yesterday-1@example.com"],
    ["attended-occurrence-yesterday-2@example.com"],
    ["enrolled-another-event@example.com"],
    ["enrolled-both-events@example.com"],
    ["enrolled-occurrence-tomorrow-1@example.com"],
    ["enrolled-occurrence-tomorrow-2@example.com"],
    ["subscribed-another-event@example.com"],
    ["subscribed-occurrence-tomorrow-1@example.com"],
    ["subscribed-occurrence-tomorrow-2@example.com"],
]

snapshots["test_message_sending_with_filters[occurrence_tomorrow_1-attended] 1"] = []

snapshots["test_message_sending_with_filters[occurrence_tomorrow_1-enrolled] 1"] = [
    ["enrolled-both-events@example.com"],
    ["enrolled-occurrence-tomorrow-1@example.com"],
]

snapshots["test_message_sending_with_filters[occurrence_tomorrow_1-invited] 1"] = [
    ["attended-another-event@example.com"],
    ["attended-occurrence-yesterday-1@example.com"],
    ["attended-occurrence-yesterday-2@example.com"],
    ["enrolled-another-event@example.com"],
    ["enrolled-occurrence-tomorrow-1@example.com"],
    ["enrolled-occurrence-tomorrow-2@example.com"],
    ["subscribed-another-event@example.com"],
    ["subscribed-occurrence-tomorrow-1@example.com"],
    ["subscribed-occurrence-tomorrow-2@example.com"],
]

snapshots[
    "test_message_sending_with_filters[occurrence_tomorrow_1-subscribed_to_free_spot_notification] 1"
] = [["subscribed-occurrence-tomorrow-1@example.com"]]

snapshots["test_message_sending_with_filters[occurrence_yesterday_1-all] 1"] = [
    ["attended-another-event@example.com"],
    ["attended-occurrence-yesterday-1@example.com"],
    ["attended-occurrence-yesterday-2@example.com"],
    ["enrolled-another-event@example.com"],
    ["enrolled-both-events@example.com"],
    ["enrolled-occurrence-tomorrow-1@example.com"],
    ["enrolled-occurrence-tomorrow-2@example.com"],
    ["subscribed-another-event@example.com"],
    ["subscribed-occurrence-tomorrow-1@example.com"],
    ["subscribed-occurrence-tomorrow-2@example.com"],
]

snapshots["test_message_sending_with_filters[occurrence_yesterday_1-attended] 1"] = [
    ["attended-occurrence-yesterday-1@example.com"]
]

snapshots["test_message_sending_with_filters[occurrence_yesterday_1-enrolled] 1"] = []

snapshots["test_message_sending_with_filters[occurrence_yesterday_1-invited] 1"] = [
    ["attended-another-event@example.com"],
    ["attended-occurrence-yesterday-1@example.com"],
    ["attended-occurrence-yesterday-2@example.com"],
    ["enrolled-another-event@example.com"],
    ["enrolled-occurrence-tomorrow-1@example.com"],
    ["enrolled-occurrence-tomorrow-2@example.com"],
    ["subscribed-another-event@example.com"],
    ["subscribed-occurrence-tomorrow-1@example.com"],
    ["subscribed-occurrence-tomorrow-2@example.com"],
]

snapshots[
    "test_message_sending_with_filters[occurrence_yesterday_1-subscribed_to_free_spot_notification] 1"
] = []
