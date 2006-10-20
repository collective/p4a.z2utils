from logging import info

def apply_patches():
    _apply_getSubObject_patch()
    _apply_DynamicView_patch()

def _apply_getSubObject_patch():
    """Apply a patch to AT < 1.4 so that traversal checks for data
    object first, then zope 3 view, then acquired attributes.
    """
    
    try:
        # don't patch if Archetypes isn't present
        from Products import Archetypes
    except:
        return
    
    try:
        from Products.Archetypes import bbb
        # the bbb module is included with AT 1.4 and higher where we do
        # not want this monkey patch to be in effect
        return
    except ImportError, e:
        pass

    info("p4a.z2utils: "
         "Fixing Archetypes Zope 3 traversal.")

    from Products.Archetypes.BaseObject import BaseObject
    
    if hasattr(BaseObject, '__p4a_orig_getSubObject'):
        # don't patch if already patched
        return

    from zope.app.publication.browser import setDefaultSkin
    from zope.app.traversing.interfaces import ITraverser, ITraversable
    from zope.component import getMultiAdapter, ComponentLookupError
    from zope.publisher.interfaces.browser import IBrowserRequest
    from Products.Five.traversable import FakeRequest
    import Products.Five.security
    from zExceptions import NotFound

    
    BaseObject.__p4a_orig_getSubObject = BaseObject.getSubObject
    
    def getSubObject(self, name, REQUEST, RESPONSE=None):
        obj = self.__p4a_orig_getSubObject(name, REQUEST, RESPONSE)
        if obj is not None:
            return obj
        
        # The following is a copy from Five's __bobo_traverse__ stuff,
        # see Products.Five.traversable for details.
        # Basically we're forcing Archetypes to look up the correct
        # Five way:
        #   1) check for data object first
        #   2) check for zope3 view 
        #   3) return nothing so that AT's default __bobo_traverse__ will use aq
        
        if not IBrowserRequest.providedBy(REQUEST):
            # Try to get the REQUEST by acquisition
            REQUEST = getattr(self, 'REQUEST', None)
            if not IBrowserRequest.providedBy(REQUEST):
                REQUEST = FakeRequest()
                setDefaultSkin(REQUEST)

        # Con Zope 3 into using Zope 2's checkPermission
        Products.Five.security.newInteraction()

        # Use the ITraverser adapter (which in turn uses ITraversable
        # adapters) to traverse to a view.  Note that we're mixing
        # object-graph and object-publishing traversal here, but Zope
        # 2 has no way to tell us when to use which...
        # TODO Perhaps we can decide on object-graph vs.
        # object-publishing traversal depending on whether REQUEST is
        # a stub or not?
        try:
            return ITraverser(self).traverse(
                path=[name], request=REQUEST).__of__(self)
        except (ComponentLookupError, LookupError,
                AttributeError, KeyError, NotFound):
            pass
        
        return None

    BaseObject.getSubObject = getSubObject



def _apply_DynamicView_patch():
    try:
        # don't patch if CMFDynamicViewFTI is not available
        from Products import CMFDynamicViewFTI
    except:
        return

    from logging import info
    info("p4a.z2utils: "
         "Extending dynamic view support with interfaces.")

    from zope.interface import Interface

    class IDynamicallyViewable(Interface):

        def getDefaultViewMethod():
            """Get the name of the default view method
            """
            
        def getAvailableViewMethods():
            """Get a tuple of registered view method names
            """
            
        def getAvailableLayouts(self):
            """Get the layouts for this object
            
            Returns tuples of tuples of view name + title.
            """


    def getDefaultViewMethod(self, context):
        """Get the default view method from the FTI
        """
        adapter = IDynamicallyViewable(context, None)
        if adapter is not None:
            return adapter.getDefaultViewMethod()
        # Fall back to old FTI information
        return str(self.default_view)

    def getAvailableViewMethods(self, context):
        """Get a tuple of registered view methods
        """
        adapter = IDynamicallyViewable(context, None)
        if adapter is not None:
            return adapter.getAvailableViewMethods()

        # Fall back to old FTI information
        methods = self.view_methods
        if isinstance(methods, basestring):
            methods = (methods,)
        return tuple(methods)

    def getAvailableLayouts(self):
        """Get the layouts registered for this object
        """
        adapter = IDynamicallyViewable(self, None)
        if adapter is not None:
            return adapter.getAvailableLayouts()

        # Fall back to old FTI information
        fti = self.getTypeInfo()
        if fti is None:
            return ()
        result = []
        method_ids = fti.getAvailableViewMethods(self)
        for mid in method_ids:
            method = getattr(self, mid, None)
            if method is not None:
                # a method might be a template, script or method
                try:
                    title = method.aq_inner.aq_explicit.title_or_id()
                except AttributeError:
                    title = mid
                result.append((mid, title))
            
        return result

    from Products.CMFDynamicViewFTI.fti import DynamicViewTypeInformation
    DynamicViewTypeInformation.getAvailableViewMethods = getAvailableViewMethods
    DynamicViewTypeInformation.getDefaultViewMethod = getDefaultViewMethod

    from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
    BrowserDefaultMixin.getAvailableLayouts = getAvailableLayouts

    from Products.CMFDynamicViewFTI import interfaces
    interfaces.IDynamicallyViewable = IDynamicallyViewable