from .tables import *
from .navigation import Navigation, ParentLink, ChildLink
from .generic import ObjectCreateView, ObjectDeleteView, ObjectDetailView, ObjectListView, ObjectTemplateView, ObjectUpdateView, ObjectTableView, DeleteView

__all__ = [
    "ChildLink",
    "ParentLink",
    "Navigation",
    
    "BaseTable",
    "CheckBoxColumn",
    "ButtonLinkColumn",
    "EmailColumn",

    "AcademHubModel",

    'DeleteView',
    'ObjectListView',
    'ObjectTableView',
    'ObjectDetailView',
    'ObjectUpdateView',
    'ObjectCreateView',
    'ObjectDeleteView',
    'ObjectTemplateView',
]