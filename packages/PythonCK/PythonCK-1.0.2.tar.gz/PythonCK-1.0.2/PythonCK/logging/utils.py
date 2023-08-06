# # For advance stacktrace
# # http://stackoverflow.com/questions/10206178/python-how-to-log-package-name

# import argparse

# #===============================================================================

# def reinit_blacklist(_): # pragma: no cover
#   """
#   Invoke this to blacklist msg send from PythonCK.Logger to be displayed
#   on other gaudi-based (LHCb) loggers.

#   http://stackoverflow.com/questions/17275334

#   """
#   # /home/khurewat/mylib/MyPythonLib/python/MyPythonLib/Logger
#   name = __file__.split('.')[0]
#   for handler in logging.Logger.root.handlers:
#     hname = str(type(handler))
#     if ('Ganga' in hname) or ('Gaudi' in hname):
#       handler.addFilter(Blacklist(name))

# #===============================================================================

# def wrap_base_parser(parser):
#   """
#   Given the specific parser, wrap it with the base implementation.
#   """
#   newparser = argparse.ArgumentParser(parents=[parser], add_help=False)
#   logger.info(newparser.parse_known_args())
#   return newparser

# #===============================================================================

# # import inspect
# # def caller_name(skip=4):
# #     """Get a name of a caller in the format module.class.method

# #        `skip` specifies how many levels of stack to skip while getting caller
# #        name. skip=1 means "who calls me", skip=2 "who calls my caller" etc.

# #        An empty string is returned if skipped levels exceed stack height
# #     """
# #     stack = inspect.stack()
# #     start = 0 + skip
# #     if len(stack) < start + 1:
# #       return ''
# #     parentframe = stack[start][0]

# #     name = []
# #     module = inspect.getmodule(parentframe)
# #     # `modname` can be None when frame is executed directly in console
# #     # TODO(techtonik): consider using __main__
# #     if module:
# #         name.append(module.__name__)
# #     # detect classname
# #     if 'self' in parentframe.f_locals:
# #         # I don't know any way to detect call from the object method
# #         # XXX: there seems to be no way to detect static method call - it will
# #         #      be just a function call
# #         name.append(parentframe.f_locals['self'].__class__.__name__)
# #     codename = parentframe.f_code.co_name
# #     if codename != '<module>':  # top level usually
# #         name.append( codename ) # function or a method
# #     del parentframe
# #     return ".".join(name)

# #==============================================================================
