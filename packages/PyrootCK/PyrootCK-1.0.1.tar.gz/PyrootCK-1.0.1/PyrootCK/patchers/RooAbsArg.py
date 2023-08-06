# from . import *

# def getattr(cls):
#   def RooAbsArg_getattr( self, key ):
#     ## By python design, the key (unmodified) should already be search on 
#     #  local instance already. Only once the search fails, getattr is a fallback.
#     raise AttributeError("%r object has no attribute %r"%(self.__class__.__name__,key))

#     ## By python design, the key (unmodified) should already be search on 
#     #  local instance already. Only once the search fails, getattr is a fallback.
#     # ## Check over these fallbacks
#     # for name in [ 'Get'+capfirst(key), 'get'+capfirst(key), 'GetListOf'+capfirst(key) ]:
#     #   # attempt with given getattr first, if any.
#     #   try:
#     #     if func_default:
#     #       return func_default(self,name)()
#     #   except AttributeError:
#     #     pass
#     #   # then, attempt with super.
#     #   try:
#     #     return super(cls,self).__getattribute__(name)()
#     #   except AttributeError:
#     #     pass
#     # raise AttributeError("%r object has no attribute %r"%(self.__class__.__name__,key))
#   return RooAbsArg_getattr


# def init(cls):
#   def RooAbsArg_init( self, *args, **kwargs ):
#     print args, kwargs
#     return cls.__init__(*args, **kwargs)
#   return RooAbsArg_init