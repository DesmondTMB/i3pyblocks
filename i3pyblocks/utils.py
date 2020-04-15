import logging

from typing import Dict, Optional

from i3pyblocks.types import Items

Log = logging.getLogger("i3pyblocks")
Log.addHandler(logging.NullHandler())


def calculate_threshold(items: Items, value: float) -> Optional[str]:
    selected_item = None

    for threshold, item in items:
        if value >= threshold:
            selected_item = item
        else:
            break

    return selected_item


def non_nullable_dict(**kwargs) -> Dict:
    return {k: v for k, v in kwargs.items() if v is not None}
