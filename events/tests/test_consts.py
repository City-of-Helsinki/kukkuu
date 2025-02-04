import pytest

from kukkuu.exceptions import KukkuuGraphQLError

from ..consts import ENROLMENT_DENIED_REASON_TO_GRAPHQL_ERROR
from ..enums import EnrolmentDeniedReason


@pytest.mark.parametrize("input", list(EnrolmentDeniedReason))
def test_enrolment_denied_reason_to_graphql_error_mapping_is_complete(
    input: EnrolmentDeniedReason,
):
    assert input in ENROLMENT_DENIED_REASON_TO_GRAPHQL_ERROR


@pytest.mark.parametrize("input", list(EnrolmentDeniedReason))
def test_enrolment_denied_reason_to_graphql_error_mapping_output_type(
    input: EnrolmentDeniedReason,
):
    assert isinstance(
        ENROLMENT_DENIED_REASON_TO_GRAPHQL_ERROR[input], KukkuuGraphQLError
    )
