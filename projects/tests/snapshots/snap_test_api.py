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
                        'name': 'Helsingin kaupunginorkesteri',
                        'singleEventsAllowed': True,
                        'translations': [
                            {
                                'languageCode': 'FI',
                                'name': 'Helsingin kaupunginorkesteri'
                            },
                            {
                                'languageCode': 'SV',
                                'name': 'Helsingfors stadsorkester'
                            },
                            {
                                'languageCode': 'EN',
                                'name': 'Helsinki Philharmonic Orchestra'
                            }
                        ],
                        'year': 2020
                    }
                },
                {
                    'node': {
                        'enrolmentLimit': 2,
                        'id': 'UHJvamVjdE5vZGU6Mg==',
                        'name': 'Helsingin Kaupunginteatteri, Suomen Kansallisteatteri, Svenska Teatern, Teatteri ILMI Ö., Q-teatteri ja Nukketeatteri Sampo',
                        'singleEventsAllowed': True,
                        'translations': [
                            {
                                'languageCode': 'EN',
                                'name': 'Helsinki City Theatre, Finnish National Theatre, Svenska Teatern, Theatre ILMI Ö., Q-teatteri and Puppet Theatre Sampo'
                            },
                            {
                                'languageCode': 'FI',
                                'name': 'Helsingin Kaupunginteatteri, Suomen Kansallisteatteri, Svenska Teatern, Teatteri ILMI Ö., Q-teatteri ja Nukketeatteri Sampo'
                            },
                            {
                                'languageCode': 'SV',
                                'name': 'Helsingfors Stadsteater, Finlands Nationalteater, Svenska Teatern, Teatteri ILMI Ö., Q-teatteri och Dockteatern Sampo'
                            }
                        ],
                        'year': 2021
                    }
                },
                {
                    'node': {
                        'enrolmentLimit': 2,
                        'id': 'UHJvamVjdE5vZGU6Mw==',
                        'name': 'Cirko - uuden sirkuksen keskus, Hotelli- ja ravintolamuseo, Suomen valokuvataiteen museo, Tanssin talo, Tanssiteatteri Hurjaruuth ja Teatterimuseo',
                        'singleEventsAllowed': True,
                        'translations': [
                            {
                                'languageCode': 'EN',
                                'name': 'Cirko – Center for New Circus, Hotel and Restaurant Museum, Finnish Museum of Photography, Dance House Helsinki, Dance Theatre Hurjaruuth and Theatre Museum'
                            },
                            {
                                'languageCode': 'FI',
                                'name': 'Cirko - uuden sirkuksen keskus, Hotelli- ja ravintolamuseo, Suomen valokuvataiteen museo, Tanssin talo, Tanssiteatteri Hurjaruuth ja Teatterimuseo'
                            },
                            {
                                'languageCode': 'SV',
                                'name': 'Cirko - Centrumet för nycirkus, Hotell- och restaurangmuseet, Dansens hus Helsingfors, Finlands fotografiska museum, Dansteatern Hurjaruuth och Teatermuseet'
                            }
                        ],
                        'year': 2022
                    }
                },
                {
                    'node': {
                        'enrolmentLimit': 2,
                        'id': 'UHJvamVjdE5vZGU6NA==',
                        'name': 'Arkkitehtuurimuseo, Designmuseo, Helsingin kaupunginmuseo, Suomen kansallismuseo, Suomen kulttuuriperintökasvatuksen seura ja Tiedemuseo Liekki',
                        'singleEventsAllowed': True,
                        'translations': [
                            {
                                'languageCode': 'EN',
                                'name': 'Museum of Finnish Architecture, Design Museum, Helsinki City Museum, National Museum of Finland, Association of Cultural Heritage Education in Finland and Helsinki University Museum Flame'
                            },
                            {
                                'languageCode': 'FI',
                                'name': 'Arkkitehtuurimuseo, Designmuseo, Helsingin kaupunginmuseo, Suomen kansallismuseo, Suomen kulttuuriperintökasvatuksen seura ja Tiedemuseo Liekki'
                            },
                            {
                                'languageCode': 'SV',
                                'name': 'Finlands Arkitekturmuseum, Designmuseet, Helsingfors stadsmuseum, Finlands Nationalmuseum, Föreningen för kulturarvsfostran i Finland och Vetenskapsmuseet Lågan'
                            }
                        ],
                        'year': 2023
                    }
                },
                {
                    'node': {
                        'enrolmentLimit': 2,
                        'id': 'UHJvamVjdE5vZGU6NQ==',
                        'name': 'Helsingin kirjasto- ja liikuntapalvelut',
                        'singleEventsAllowed': True,
                        'translations': [
                            {
                                'languageCode': 'EN',
                                'name': 'Helsinki City Library and Helsinki City Sports Services'
                            },
                            {
                                'languageCode': 'FI',
                                'name': 'Helsingin kirjasto- ja liikuntapalvelut'
                            },
                            {
                                'languageCode': 'SV',
                                'name': 'Helsingfors biblioteks– och idrottstjänster'
                            }
                        ],
                        'year': 2024
                    }
                },
                {
                    'node': {
                        'enrolmentLimit': 2,
                        'id': 'UHJvamVjdE5vZGU6Ng==',
                        'name': 'HAM Helsingin taidemuseo, Amos Rex, Sointi Jazz Orchestra, UMO Helsinki Jazz Orchestra ja Kansallisgalleria: Ateneumin taidemuseo, Nykytaiteen museo Kiasma ja Sinebrychoffin taidemuseo',
                        'singleEventsAllowed': True,
                        'translations': [
                            {
                                'languageCode': 'EN',
                                'name': 'HAM Helsinki Art Museum, Amos Rex, Sointi Jazz Orchestra, UMO Helsinki Jazz Orchestra, Ateneum Art Museum, Museum of Contemporary Art Kiasma and Sinebrychoff Art Museum'
                            },
                            {
                                'languageCode': 'FI',
                                'name': 'HAM Helsingin taidemuseo, Amos Rex, Sointi Jazz Orchestra, UMO Helsinki Jazz Orchestra ja Kansallisgalleria: Ateneumin taidemuseo, Nykytaiteen museo Kiasma ja Sinebrychoffin taidemuseo'
                            },
                            {
                                'languageCode': 'SV',
                                'name': 'HAM Helsingfors konstmuseum, Amos Rex, Sointi Jazz Orchestra, UMO Helsinki Jazz Orchestra och Nationalgalleriet dvs. Ateneum, Kiasma och Konstmuseet Sinebrychoff'
                            }
                        ],
                        'year': 2025
                    }
                }
            ]
        }
    }
}
