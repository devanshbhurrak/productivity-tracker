import math
from typing import Tuple


def paginate_params(page: int, page_size: int, max_page_size: int = 100) -> Tuple[int, int]:
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 1
    if page_size > max_page_size:
        page_size = max_page_size
    offset = (page - 1) * page_size
    limit = page_size
    return offset, limit


def build_pagination_meta(page: int, page_size: int, total: int) -> dict:
    total_pages = math.ceil(total / page_size) if page_size else 0
    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
    }
