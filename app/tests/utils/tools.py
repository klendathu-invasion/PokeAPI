from ... import models


def get_levels(session, role: str, user: models.user.User, owner: str | None = None):
    levels = {}
    if (role == "owner" and user.is_pro and owner == "pro") or (
        role == "possessor" and not user.is_pro and owner == "client"
    ):
        levels["user_id"] = user.id
    if role == "member" and user.is_pro:
        levels["shop_id"] = user.shop_ids[0]
    return levels


# add member
