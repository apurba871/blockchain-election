from permission import Permission
from .rules import UserRule, AdminRule

class UserPermission(Permission):
  def rule():
    return UserRule()
  
class AdminPermission(Permission):
  def rule():
    return AdminRule()