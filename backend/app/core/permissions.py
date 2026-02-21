from functools import wraps
from fastapi import HTTPException, status, Request
from backend.app.models.enums import Role

# Hierarchy where lower index means more privileges
ROLE_HIERARCHY = {
    Role.SUPER_ADMIN: 0,
    Role.ORG_ADMIN: 1,
    Role.HIRING_MANAGER: 2,
    Role.RECRUITER: 3,
    Role.VIEWER: 4,
    Role.CANDIDATE: 5
}

def require_role(minimum_role: Role):
    """
    Dependency to enforce Role-Based Access Control (RBAC).
    Checks if the current user's role index is <= the required role's index.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Expecting request to contain current_user set by auth middleware
            request: Request = kwargs.get('request')
            if not request:
                # Search through args if request is positional
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
            
            if not request or not hasattr(request.state, "user"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated"
                )
            
            user_role = request.state.user.role
            
            if ROLE_HIERARCHY.get(user_role, 99) > ROLE_HIERARCHY.get(minimum_role, 99):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Requires {minimum_role.value} or higher."
                )
                
            return await func(*args, **kwargs)
        return wrapper
    return decorator
