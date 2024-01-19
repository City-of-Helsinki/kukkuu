# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_children_endpoint 1"] = [
    {
        "birth_year": 2020,
        "child_birthyear_postal_code_guardian_emails_hash": "3b31e6ff1604056d31986fb1bca8897f7bcbb391d79790aa051d0a89d62b5834",
        "child_name_birthyear_postal_code_guardian_emails_hash": "4069c997d8143d91d7f118bff0b82f1b2883ddb16481c65f56ef9c57439374db",
        "contact_language": "eng",
        "languages_spoken_at_home": [],
        "postal_code": "33333",
        "registration_date": "2021-04-05",
    },
    {
        "birth_year": 2021,
        "child_birthyear_postal_code_guardian_emails_hash": "72fa21cf7750f88d4085086b143a56ec6ba196c98693f1e4e7f39b76f9e2803e",
        "child_name_birthyear_postal_code_guardian_emails_hash": "e58f738060e22e10d91ab2c8b92ba59cbba4a131b989006b3c505542e42cd7f1",
        "contact_language": "fin",
        "languages_spoken_at_home": ["fin", "__OTHER__"],
        "postal_code": "11111",
        "registration_date": "2021-02-02",
    },
    {
        "birth_year": 2021,
        "child_birthyear_postal_code_guardian_emails_hash": "db91f2de11ce26e8e49e179cd27e77805acc984af98aabab9d45987cc45c255c",
        "child_name_birthyear_postal_code_guardian_emails_hash": "e44d5dbee7e5f8d81fad5b9940da627a0844fce197f2b737b7476a38718acf21",
        "contact_language": "swe",
        "languages_spoken_at_home": ["__OTHER__"],
        "postal_code": "22222",
        "registration_date": "2021-03-03",
    },
    {
        "birth_year": 2020,
        "child_birthyear_postal_code_guardian_emails_hash": "fe3aac27294ec2fa750bdf5eb4807c04224f1cc7863485e58a6941546261613f",
        "child_name_birthyear_postal_code_guardian_emails_hash": "f3c34690d0ab00f7f367e8ff44dd94529c50916bb4088e23f23501b2d8085790",
        "contact_language": "swe",
        "languages_spoken_at_home": [],
        "postal_code": "44444",
        "registration_date": "2021-04-06",
    },
]
