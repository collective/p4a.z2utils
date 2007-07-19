from Products.CMFCore import utils as cmfutils
from zope import interface

try:
    from zope.component.interface import interfaceToName
except ImportError:
    def interfaceToName(context, iface):
        # context argument only used to maintain api compatibility with
        # interfaceToName from zope 3.3
        return iface.__module__ + '.' + iface.__name__

def remove_marker_ifaces(context, ifaces): 
    """Remove the given interfaces from all objects using a catalog
    query.  context needs to either be the portal or be properly aq wrapped
    to allow for cmf catalog tool lookup.  ifaces can be either a single
    interface or a sequence of interfaces.
    """

    if not isinstance(ifaces, (tuple, list)):
        ifaces = [ifaces]

    count = 0
    for iface in ifaces:
        for obj in objs_with_iface(context, iface):
            count += 1
            provided = interface.directlyProvidedBy(obj)
            interface.directlyProvides(obj, provided - iface)
    return count

def objs_with_iface(context, iface):
    """Return all objects in the system as found by the nearest portal
    catalog that provides the given interface.  The result will be a generator
    for scalability reasons.

      >>> 
    """



    catalog = cmfutils.getToolByName(context, 'portal_catalog')

    for brain in catalog(object_provides=interfaceToName(context, iface)):
        obj = brain.getObject()
        if iface in interface.directlyProvidedBy(obj):
            yield brain.getObject()
