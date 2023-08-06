
class ApiNotAuthenticated(Exception):
    pass


class NoApiTokenFound(Exception):
    pass

class PermissionScopeDenied(Exception):
    pass

class RateLimitReached(Exception):
    pass
