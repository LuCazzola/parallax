from unittest import mock

from client.grpc import wait_before_retry


def test_waits_half_a_second():
    with mock.patch("time.sleep") as sleep:
        wait_before_retry(500)
    sleep.assert_called_once_with(0.5)
