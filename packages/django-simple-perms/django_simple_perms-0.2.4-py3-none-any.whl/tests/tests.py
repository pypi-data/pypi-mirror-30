import uuid
from django.test import TestCase
from django.contrib.auth.models import User  # noqa
from simple_perms import PermissionLogic
import simple_perms.registry


def custom_global_default_permission(user, obj, perm):
    import pdb
    pdb.set_trace()
    return True


class MainTestSuite(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user('user1', 'user1@users.org', 'password')
        self.user2 = User.objects.create_user('user2', 'user2@users.org', 'password')

    def test_do_this(self):
        self.assertTrue(self.user1.has_perm('test_app.always_true'))

    def test_specific_user_attribute(self):
        self.user1.specific_user_attribute = True
        self.assertTrue(self.user1.has_perm('test_app.user_dependant_perm'))
        self.user1.specific_user_attribute = False
        self.assertFalse(self.user1.has_perm('test_app.user_dependant_perm'))

    def test_specific_object_attribute(self):
        self.assertTrue(self.user1.has_perm('test_app.object_dependant_perm', {'x': True}))
        self.assertFalse(self.user1.has_perm('test_app.object_dependant_perm', {'x': False}))

    def test_default_permission(self):
        self.user1.can_default_permission = False
        self.assertFalse(self.user1.has_perm('test_app.undefined_perm'))
        self.user1.can_default_permission = True
        self.assertTrue(self.user1.has_perm('test_app.undefined_perm'))

    def test_global_default_permission(self):
        self.assertFalse(self.user1.has_perm('test_app_global_default_permission.undefined_perm'))
        self.assertFalse(self.user1.has_perm('unregistered_app.undefined_perm'))

        # TODO : test modified global permission default
        # with self.settings(SIMPLE_PERMS_GLOBAL_DEFAULT_PERMISSION='tests.tests.custom_global_default_permission'):
        #     self.assertTrue(self.user1.has_perm('test_app_global_default_permission.undefined_perm'))
        #     self.assertTrue(self.user1.has_perm('unregistered_app.undefined_perm'))


class TestPermissionLogic(PermissionLogic):
    pass


class RegistryTestSuite(TestCase):

    def setUp(self):
        self.app_name = 'app_name_%s' % uuid.uuid4().hex
        simple_perms.registry.register(self.app_name, TestPermissionLogic)

    def test_register(self):
        self.assertIn(self.app_name, simple_perms.registry._registry.keys())
        self.assertIsInstance(simple_perms.registry._registry[self.app_name], TestPermissionLogic)

    def test_get_app_logic(self):
        self.assertIsInstance(simple_perms.registry.get_app_logic(self.app_name), TestPermissionLogic)
