from collections.abc import Callable
from flask import Blueprint
from typing import Any

class Builder:
    def __init__(self, name: str) -> None:
        """RESTful Builder, helper class to create a RESTful endpoint.

        :param str name: The name of the endpoint (just the name, no '/')
        """
        self.name = name.split('/')[-1]
        self.bp = Blueprint(self.name, __name__)
    
    def bind(self, login: Callable | None = None, refresh: Callable | None = None, getAll: Callable | None = None, getMe: Callable | None = None, getOne: Callable[[str], Any] | None = None, create: Callable | None = None, modify: Callable[[str], Any] | None = None, delete: Callable[[str | None], Any] | None = None) -> 'Builder':
        """Binds all endpoints in one function.

        :param Callable | None getAll: Callback to get all resources.
        :param Callable | None getOne: Callback to get one resource.
        :param Callable | None create: Callback to create a resource.
        :param Callable | None modify: Callback to modify a resource.
        :param Callable | None delete: Callback to delete a resource.
        :param Callable | None login: Callback to login.
        :raises RuntimeError: Raised if no callback is given.
        """
        if login:
            @self.bp.post('/login')
            def w0() -> dict: return login()
        if refresh:
            @self.bp.get('/refresh')
            def w1() -> dict: return refresh()
        if getAll:
            @self.bp.get('/')
            def w2() -> dict: return getAll()
        if getMe:
            @self.bp.get('/me')
            def w3() -> dict: return getMe()
        if getOne:
            @self.bp.get('/<id>')
            def w4(id: Any) -> dict: return getOne(id)
        if create:
            @self.bp.post('/')
            def w5() -> dict: return create()
        if modify:
            @self.bp.put('/<id>')
            @self.bp.patch('/<id>')
            def w6(id: Any) -> dict: return modify(id)
        if delete:
            @self.bp.delete('/')
            @self.bp.delete('/<id>')
            def w7(id: Any | None = None) -> dict: return delete(id)
        if not login and \
           not getAll and \
           not getMe and \
           not getOne and \
           not create and \
           not modify and \
           not delete: raise RuntimeError('You need to bind at least one of the callbacks.')
        return self
    
    def getAll(self, callback: Callable) -> 'Builder':
        """Get all resources.

        :param Callable callback: Callback to execute.
        """
        @self.bp.get('/')
        def wrapper(): return callback()
        return self
    
    def getOne(self, callback: Callable) -> 'Builder':
        """Get one resource.

        :param Callable callback: Callback to execute.
        """
        @self.bp.get('/<id>')
        def wrapper(id: Any): return callback(id)
        return self
    
    def create(self, callback: Callable) -> 'Builder':
        """Create a resource.

        :param Callable callback: Callback to execute.
        """
        @self.bp.post('/')
        def wrapper(): return callback()
        return self
    
    def modify(self, callback: Callable) -> 'Builder':
        """Modify a resource.

        :param Callable callback: Callback to execute.
        """
        @self.bp.put('/<id>')
        @self.bp.patch('/<id>')
        def wrapper(id: Any): return callback(id)
        return self
    
    def delete(self, callback: Callable) -> 'Builder':
        """Delete a resource.

        :param Callable callback: Callback to execute.
        """
        @self.bp.delete('/<id>')
        def wrapper(id: Any): return callback(id)
        return self
