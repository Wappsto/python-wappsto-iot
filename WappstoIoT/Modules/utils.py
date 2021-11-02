from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import UUID4
from pydantic import HttpUrl

from WappstoIoT.Schema.IoTSchema import WappstoObjectType


def dictDiff(olddict: Dict[Any, Any], newdict: Dict[Any, Any]):
    """Find & return what have updated from old to new dictionary."""
    return dict(set(newdict.items() - set(olddict.items())))
