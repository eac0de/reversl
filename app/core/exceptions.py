from fastapi import Response


class ResponseException(Exception):
    def __init__(self, response: Response):
        self.response = response
