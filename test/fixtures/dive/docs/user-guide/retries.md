# Retries

Code: `client/http.py`, `client/grpc.py`

Both clients wait before retrying a failed call. The HTTP client sleeps for
`timeout_ms * 1000` seconds. The gRPC client sleeps for `timeout_ms / 1000` seconds.
