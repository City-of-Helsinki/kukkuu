# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_children_endpoint 1'] = [
    {
        'birthyear': 2020,
        'child_birthyear_postal_code_guardian_emails_hash': '3b78fc2b60381829414bd2bd9ea53e90123d9cd7faeb35f86f5038d669dd96e0',
        'child_name_birthyear_postal_code_guardian_emails_hash': 'bd94f9a87d842f6889f10aa72528a273c27fb864fe7b14b7b38b2b37a59b615a',
        'contact_language': 'eng',
        'is_obsolete': False,
        'languages_spoken_at_home': [
        ],
        'postal_code': '33333',
        'registration_date': '2021-04-05'
    },
    {
        'birthyear': 2021,
        'child_birthyear_postal_code_guardian_emails_hash': 'd9653e3210babd7c8d6094f069ddfbf790d6b16d368d0b14e0d4f9d1d2eed8aa',
        'child_name_birthyear_postal_code_guardian_emails_hash': 'cde8b66cfb17f9dd1e3a27b34ced099567555c09ac53ab8d96eb6f108b481a78',
        'contact_language': 'fin',
        'is_obsolete': False,
        'languages_spoken_at_home': [
            'fin',
            '__OTHER__'
        ],
        'postal_code': '11111',
        'registration_date': '2021-02-02'
    },
    {
        'birthyear': 2021,
        'child_birthyear_postal_code_guardian_emails_hash': '73471fad7bbcffa243a695f211ffd2c0ddb89531d747548709c3677ecbe4a0cc',
        'child_name_birthyear_postal_code_guardian_emails_hash': 'c056d2e1b6ca2ab0189ce068567cb6d3951928283e8ebbb384ec20d3a85f632e',
        'contact_language': 'swe',
        'is_obsolete': False,
        'languages_spoken_at_home': [
            '__OTHER__'
        ],
        'postal_code': '22222',
        'registration_date': '2021-03-03'
    },
    {
        'birthyear': 2020,
        'child_birthyear_postal_code_guardian_emails_hash': 'f1694b9c7d7a45c8606d9506f171025079940fcc97d5e125e1cc73495461f378',
        'child_name_birthyear_postal_code_guardian_emails_hash': '92d10305295a1210620ae3158c5aeecc24d9018be279042e8226d120cbfdb978',
        'contact_language': 'eng',
        'is_obsolete': False,
        'languages_spoken_at_home': [
        ],
        'postal_code': '44444',
        'registration_date': '2021-04-06'
    }
]

snapshots['test_event_groups_endpoint 1'] = [
    {
        'attended_count': 0,
        'capacity': 20,
        'enrolment_count': 1,
        'events_count': 1,
        'id': 1,
        'name': {
            'en': '',
            'fi': 'Example Event Group 1',
            'sv': ''
        },
        'project': {
            'id': 1,
            'year': 2020
        },
        'url': 'http://testserver/reports/event-group/1/'
    },
    {
        'attended_count': 0,
        'capacity': 0,
        'enrolment_count': 0,
        'events_count': 0,
        'id': 2,
        'name': {
            'en': 'Example Event Group 2 (en)',
            'fi': 'Example Event Group 2 (fi)',
            'sv': 'Example Event Group 2 (sv)'
        },
        'project': {
            'id': 1,
            'year': 2020
        },
        'url': 'http://testserver/reports/event-group/2/'
    },
    {
        'attended_count': 0,
        'capacity': 0,
        'enrolment_count': 0,
        'events_count': 0,
        'id': 3,
        'name': {
            'en': 'Example Event Group 3 (en)',
            'fi': 'Example Event Group 3 (fi)',
            'sv': 'Example Event Group 3 (sv)'
        },
        'project': {
            'id': 1,
            'year': 2020
        },
        'url': 'http://testserver/reports/event-group/3/'
    },
    {
        'attended_count': 0,
        'capacity': 0,
        'enrolment_count': 0,
        'events_count': 0,
        'id': 4,
        'name': {
            'en': 'Example Event Group 4 (en)',
            'fi': 'Example Event Group 4 (fi)',
            'sv': 'Example Event Group 4 (sv)'
        },
        'project': {
            'id': 1,
            'year': 2020
        },
        'url': 'http://testserver/reports/event-group/4/'
    },
    {
        'attended_count': 0,
        'capacity': 0,
        'enrolment_count': 0,
        'events_count': 0,
        'id': 5,
        'name': {
            'en': 'Example Event Group 5 (en)',
            'fi': 'Example Event Group 5 (fi)',
            'sv': 'Example Event Group 5 (sv)'
        },
        'project': {
            'id': 1,
            'year': 2020
        },
        'url': 'http://testserver/reports/event-group/5/'
    }
]

snapshots['test_event_groups_retrieve_endpoint 1'] = {
    'attended_count': 1,
    'capacity': 20,
    'enrolment_count': 2,
    'events_count': 1,
    'id': 1,
    'name': {
        'en': 'Example Event Group (en)',
        'fi': 'Example Event Group (fi)',
        'sv': 'Example Event Group (sv)'
    },
    'project': {
        'id': 1,
        'year': 2020
    },
    'url': 'http://testserver/reports/event-group/1/'
}

snapshots['test_events_endpoint 1'] = [
    {
        'attended_count': 0,
        'capacity': 40,
        'enrolment_count': 2,
        'event_group': {
            'id': 1,
            'url': 'http://testserver/reports/event-group/1/'
        },
        'id': 1,
        'name': {
            'en': '',
            'fi': 'Write century spring never skill down subject town.',
            'sv': ''
        },
        'occurrences': [
            {
                'attended_count': 0,
                'capacity': 20,
                'enrolment_count': 2,
                'id': 1,
                'time': '2021-04-05T02:00:00+03:00',
                'venue': {
                    'id': 1,
                    'url': 'http://testserver/reports/venue/1/'
                }
            },
            {
                'attended_count': 0,
                'capacity': 20,
                'enrolment_count': 0,
                'id': 2,
                'time': '2021-04-05T02:00:00+03:00',
                'venue': {
                    'id': 2,
                    'url': 'http://testserver/reports/venue/2/'
                }
            }
        ],
        'occurrences_count': 2,
        'project': {
            'id': 1,
            'year': 2020
        },
        'ticket_system': 'internal'
    },
    {
        'attended_count': 0,
        'capacity': 80,
        'enrolment_count': 2,
        'event_group': None,
        'id': 2,
        'name': {
            'en': '',
            'fi': 'People sense knowledge stock subject.',
            'sv': ''
        },
        'occurrences': [
            {
                'attended_count': 0,
                'capacity': 40,
                'enrolment_count': 2,
                'id': 3,
                'time': '2021-04-05T02:00:00+03:00',
                'venue': {
                    'id': 3,
                    'url': 'http://testserver/reports/venue/3/'
                }
            },
            {
                'attended_count': 0,
                'capacity': 40,
                'enrolment_count': 0,
                'id': 4,
                'time': '2021-04-05T02:00:00+03:00',
                'venue': {
                    'id': 4,
                    'url': 'http://testserver/reports/venue/4/'
                }
            }
        ],
        'occurrences_count': 2,
        'project': {
            'id': 1,
            'year': 2020
        },
        'ticket_system': 'internal'
    }
]

snapshots['test_venue_retrieve_endpoint 1'] = {
    'address': {
        'en': 'Example Address (en)',
        'fi': 'Example Address (fi)',
        'sv': 'Example Address (sv)'
    },
    'id': 1,
    'name': {
        'en': 'Example Venue (en)',
        'fi': 'Example Venue (fi)',
        'sv': 'Example Venue (sv)'
    },
    'project': {
        'id': 1,
        'year': 2020
    },
    'url': 'http://testserver/reports/venue/1/'
}

snapshots['test_venues_endpoint 1'] = [
    {
        'address': {
            'en': 'Example Address 1 (en)',
            'fi': 'Example Address 1 (fi)',
            'sv': 'Example Address 1 (sv)'
        },
        'id': 1,
        'name': {
            'en': 'Example Venue 1 (en)',
            'fi': 'Example Venue 1 (fi)',
            'sv': 'Example Venue 1 (sv)'
        },
        'project': {
            'id': 1,
            'year': 2020
        },
        'url': 'http://testserver/reports/venue/1/'
    },
    {
        'address': {
            'en': 'Example Address 2 (en)',
            'fi': 'Example Address 2 (fi)',
            'sv': 'Example Address 2 (sv)'
        },
        'id': 2,
        'name': {
            'en': 'Example Venue 2 (en)',
            'fi': 'Example Venue 2 (fi)',
            'sv': 'Example Venue 2 (sv)'
        },
        'project': {
            'id': 1,
            'year': 2020
        },
        'url': 'http://testserver/reports/venue/2/'
    },
    {
        'address': {
            'en': 'Example Address 3 (en)',
            'fi': 'Example Address 3 (fi)',
            'sv': 'Example Address 3 (sv)'
        },
        'id': 3,
        'name': {
            'en': 'Example Venue 3 (en)',
            'fi': 'Example Venue 3 (fi)',
            'sv': 'Example Venue 3 (sv)'
        },
        'project': {
            'id': 1,
            'year': 2020
        },
        'url': 'http://testserver/reports/venue/3/'
    },
    {
        'address': {
            'en': 'Example Address 4 (en)',
            'fi': 'Example Address 4 (fi)',
            'sv': 'Example Address 4 (sv)'
        },
        'id': 4,
        'name': {
            'en': 'Example Venue 4 (en)',
            'fi': 'Example Venue 4 (fi)',
            'sv': 'Example Venue 4 (sv)'
        },
        'project': {
            'id': 1,
            'year': 2020
        },
        'url': 'http://testserver/reports/venue/4/'
    },
    {
        'address': {
            'en': 'Example Address 5 (en)',
            'fi': 'Example Address 5 (fi)',
            'sv': 'Example Address 5 (sv)'
        },
        'id': 5,
        'name': {
            'en': 'Example Venue 5 (en)',
            'fi': 'Example Venue 5 (fi)',
            'sv': 'Example Venue 5 (sv)'
        },
        'project': {
            'id': 1,
            'year': 2020
        },
        'url': 'http://testserver/reports/venue/5/'
    }
]
