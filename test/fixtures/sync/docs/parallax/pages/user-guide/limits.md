# Limits

Code: `src/app/config.py`

Uploads are capped at 20 MB, which keeps the upload workers responsive. Login tokens last
one hour, so people are not asked to sign in repeatedly during a working session.
