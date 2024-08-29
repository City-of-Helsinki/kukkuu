# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_project_query_normal_user 1'] = {
    'data': {
        'project': {
            'enrolmentLimit': 2,
            'id': 'UHJvamVjdE5vZGU6MQ==',
            'name': 'Testiprojekti',
            'singleEventsAllowed': True,
            'translations': [
                {
                    'languageCode': 'FI',
                    'name': 'Testiprojekti'
                }
            ],
            'year': 2020
        }
    }
}

snapshots['test_projects_query_normal_user 1'] = {
    'data': {
        'projects': {
            'edges': [
                {
                    'node': {
                        'enrolmentLimit': 2,
                        'id': 'UHJvamVjdE5vZGU6MQ==',
                        'name': 'Testiprojekti',
                        'singleEventsAllowed': True,
                        'translations': [
                            {
                                'languageCode': 'FI',
                                'name': 'Testiprojekti'
                            }
                        ],
                        'year': 2020
                    }
                }
            ]
        }
    }
}
