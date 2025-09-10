import pytest
import respx
from httpx import Response

from pesapal_client import PesapalException


def test_pesapal_error_raises(client_sandbox):
    with respx.mock(base_url=client_sandbox._base_url) as mock:
        mock.get("/Transactions/GetTransactionStatus").mock(
            return_value=Response(
                200,
                json={
                    "error": {
                        "type": "InvalidRequest",
                        "code": "500",
                        "message": "Invalid tracking ID",
                    },
                    "status": "500",
                },
            )
        )

        with pytest.raises(PesapalException) as exc:
            client_sandbox.one_time_payment.get_payment_order_status("bad_id")
        assert exc.value.code == "500"
