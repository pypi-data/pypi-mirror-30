from typing import Dict, Tuple, List
from collections import OrderedDict
from sqlalchemy.ext.declarative.api import DeclarativeMeta
from sqlalchemy.sql.elements import BinaryExpression


class StarDocMap():
    """ A class which defines a StarDocMap object
    """
    join_order: List[Tuple[DeclarativeMeta, BinaryExpression]]
    resource_map: OrderedDict[str, Dict[str, object]]
    path_params: Dict[str, object]
    query_params: Dict[str, object]
