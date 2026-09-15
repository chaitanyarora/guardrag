ROLE_PERMISSIONS = {
    "finance": ["finance", "general"],
    "marketing": ["marketing", "general"],
    "hr": ["hr", "general"],
    "engineering": ["engineering", "general"],
    "executive": [
        "finance",
        "marketing",
        "hr",
        "engineering",
        "general",
    ],
    "employee": ["general"],
}


def get_allowed_departments(role: str) -> list[str]:
    """
    Return the departments that a role is allowed to access.
    """
    return ROLE_PERMISSIONS.get(role, [])