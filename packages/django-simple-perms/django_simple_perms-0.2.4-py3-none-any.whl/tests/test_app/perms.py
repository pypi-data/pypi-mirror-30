from simple_perms import register, PermissionLogic


class TestAppPermissionLogic(PermissionLogic):

    def always_true(self, user, obj, perm):
        return True

    def user_dependant_perm(self, user, obj, perm):
        return user.specific_user_attribute

    def object_dependant_perm(self, user, obj, perm):
        return obj.get('x')

    def default_permission(self, user, obj, perm):
        return user.can_default_permission

register('test_app', TestAppPermissionLogic)


class GlobalDefaultPermissionPermissionLogic(PermissionLogic):
    pass

register('test_app_global_default_permission', GlobalDefaultPermissionPermissionLogic)
