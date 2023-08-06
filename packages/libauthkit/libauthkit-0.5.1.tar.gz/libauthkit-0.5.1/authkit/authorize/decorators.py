#!/usr/bin/env python
"""WSGI adaptors version 2 for integrating AuthKit with Django.

This module is based on the ``powerpack_adaptors.py`` extension, and
adds extra customizations for Django.

Copyright (C) 2010-2012 Etienne Robillard <erob@gthcfoundation.org>
All rights reserved

In the AuthKit model permissions are handled by ``Permission`` objects.
Authorization objects are used to check permissions and to raise
``NotAuthenticatedError`` or ``NotAuthorizedError`` if there is no user or the
user is not authorized. The execeptions are converted to HTTP responses which
are then intercepted and handled by the authentication middleware.

The way permissions objects should be checked depends on where abouts in the
application stack the check occurs and so different authorization objects exist
to make checks at different parts of the stack. You can of course create 
your own permission objects to be authorized by the middleware and decorator
defined here. See the permissions docs or the AuthKit manual for more 
information.

Framework implementors might also create their own implementations of AuthKit
authorization objects. For example the ``authkit.pylons_adaptors`` module
contains some Pylons-specific authorization objects which you'll want to use
if you are using AuthKit with Pylons.

For an example of how to use permission objects have a look at the
``AuthorizeExampleApp`` class in the ``authorize.py`` example in the ``examples``
directory or have a look at the AuthKit manual.
"""


import logging
log = logging.getLogger(__name__)

from functools import wraps

from .exc import *
from .middleware import middleware



__all__ = ['authorize', 'authorized']

def authorize(perm, errorHandler=Exception):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapper(*args, **kwargs):
            request = args[0]
            user = request.environ.get('REMOTE_USER', None)
            if user is None:
                log.debug("User not authenticated.")
                #return errorHandler('You must authenticate first.')
                raise Exception("You must authenticate first.")
                # use ``func`` as the start_response callback
            else:
                log.debug("Authorizing user %s" % user)
                def on_authorize(environ, start_response):
                    try:
                        result = perm.check(request, environ, start_response)
                    except Exception as e:
                        log.debug("ERROR: %s" % e)
                        return False
                    else:
                        return result
                is_authorized = bool(on_authorize(request.environ.copy(), view_func))
                if is_authorized:
                    return view_func(request, **kwargs)
                else:
                    log.debug("User not authorized")
                    return errorHandler("You're not authorized to see this page!")
        return _wrapper
        #return wraps(view_func)(_wrapper, **kwargs)
    return decorator

def authorized(environ, permission):

    try:
        middleware(environ, permission)
    except (NotAuthorizedError, NotAuthenticatedError):
        return False
    else:
        return True
