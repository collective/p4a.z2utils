from Products.CMFCore import utils as cmfutils
from Products.CMFPlone import CatalogTool
from zope import interface

def interfaceToName(context, iface):
    # context argument only used to maintain api compatibility with
    # interfaceToName from zope 3.3
    return iface.__module__ + '.' + iface.__name__

# Plone 3 provides this so we want to use plone 3's instead if possible
if not hasattr(CatalogTool, 'object_provides'):
    def object_provides(object, portal, **kw):
        return [interfaceToName(portal, i)
                for i in interface.providedBy(object).flattened()]

    CatalogTool.registerIndexableAttribute('object_provides', object_provides)

def ensure_object_provides(context):
    catalog = cmfutils.getToolByName(context, 'portal_catalog')
    if 'object_provides' not in catalog.indexes():
        catalog.manage_addIndex('object_provides', 'KeywordIndex')
        catalog.manage_reindexIndex('object_provides')
