from abc import ABCMeta, abstractmethod
import hashlib
import random
import string


class Permission(object):
    VIEW = "view"
    CREATE = "create"
    EDIT = "edit"
    REMOVE = "remove"


class UserCreatedEvent(object):
    def __init__(self, user):
        self.user = user


class UserUpdatedEvent(UserCreatedEvent):
    pass


class UserRemovedEvent(UserCreatedEvent):
    pass


class GrantEvent(object):
    def __init__(self, role, resource, permission):
        self.role = role
        self.resource = resource
        self.permission = permission


class RevokeEvent(GrantEvent):
    pass


class AuthenticationEvent(object):
    def __init__(self, username, success):
        self.username = username
        self.success = success


class UserManager(metaclass=ABCMeta):
    @abstractmethod
    def authenticate(self, username, password):
        pass

    @abstractmethod
    def create(self, username, password):
        pass

    @abstractmethod
    def updatePassword(self, user, password):
        pass

    @abstractmethod
    def update(self, user):
        pass

    @abstractmethod
    def find(self, user_id):
        pass

    @abstractmethod
    def find_by(self, **kwars):
        pass

    @abstractmethod
    def remove(self, user):
        pass

    @abstractmethod
    def enable(self, user, status):
        pass

    @abstractmethod
    def grant(self, role, resource, permission):
        pass

    @abstractmethod
    def revoke(self, role, resource, permission):
        pass

    @abstractmethod
    def is_granted(self, role, resource, permission):
        pass

    @abstractmethod
    def role_permissions(self, role):
        pass

    @abstractmethod
    def resource_permissions(self, resource):
        pass

    @abstractmethod
    def notify(self, event):
        pass

    def random_string(self, size=32):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(size))

    def generate_salt(self):
        m = hashlib.sha512()
        m.update(self.random_string().encode())
        return m.hexdigest()

    def encode_password(self, password, salt=""):
        m = hashlib.sha512()
        m.update((password + salt).encode())
        return m.hexdigest()


