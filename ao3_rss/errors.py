# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2023 Kenneth Chew

"""
Implementations of errors that can be provided to the user.
"""
from flask import make_response, render_template


class ErrorResponse:
    """An error response that can be provided to the user."""

    def __init__(self, code: int, template: str):
        self.code = code
        self.template = template
        self.response = None

    def make_response(self):
        """Returns a response for this error."""
        if self.response is None:
            self.response = make_response(render_template(self.template), self.code)
        return self.response


AuthRequiredResponse = ErrorResponse(401, "auth_required.html")
NoSuchSeriesResponse = ErrorResponse(404, "no_series.html")
NoSuchWorkResponse = ErrorResponse(404, "no_work.html")
UnknownErrorResponse = ErrorResponse(500, "unknown_error.html")
BadGatewayResponse = ErrorResponse(502, "bad_gateway.html")
TimeoutResponse = ErrorResponse(504, "timeout.html")
ExplicitContentResponse = ErrorResponse(403, "explicit_block.html")
