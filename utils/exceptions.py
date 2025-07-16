from fastapi import HTTPException

from config import settings
from connections.slack import Slack


class EmptySizeQueryNotAllowed(HTTPException):
    def __init__(self) -> None:
        message = "size field cannot be 0"
        status_code = 400
        super().__init__(status_code=status_code, detail=message)


class QueryResultTooLarge(HTTPException):
    def __init__(self) -> None:
        message = "Query result is too large"
        status_code = 400
        super().__init__(status_code=status_code, detail=message)


class APIGenericError(Exception):
    def __init__(self, message: str, body_payload=None, *args) -> None:
        super().__init__(message, *args)

        slack = Slack()
        if not settings.IS_LOCAL and body_payload:
            payload = slack.create_slack_post_error(
                request_post=body_payload, message=message
            )

            slack.do_slack_post(
                url_slack=body_payload.slack_post_error.slack_channel_name,
                payload=payload,
            )
