from typing import TypedDict, List
from fastapi import APIRouter


class Route(TypedDict):
    router: APIRouter
    prefix: str
    tags: List[str]
