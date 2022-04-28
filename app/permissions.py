from permission import Permission
from .rules import UserRule, AdminRule

class UserPermission(Permission):
  def rule(self):
    return UserRule()
  
class AdminPermission(Permission):
  def rule(self):
    return AdminRule()