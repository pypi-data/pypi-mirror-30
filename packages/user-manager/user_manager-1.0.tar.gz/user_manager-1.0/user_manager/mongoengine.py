from mongoengine import Document, StringField, BooleanField, ListField, DoesNotExist
from user_manager.user_manager import UserManager, GrantEvent, AuthenticationEvent, UserCreatedEvent, UserRemovedEvent, UserUpdatedEvent, RevokeEvent
import logging


class User(Document):

    username = StringField(required=True, unique=True)
    password = StringField(required=True)
    salt = StringField(required=True)
    enabled = BooleanField(default=True)
    roles = ListField()


class Permission(Document):

    role = StringField(required=True)
    resource = StringField(required=True)
    permission = StringField(required=True)


class MongoUserManager(UserManager):
    
    def __init__(self, user_model=User, permission_model=Permission):
        self.user_model = user_model
        self.permission_model = permission_model
        
    def authenticate(self, username, password):
        try:
            u = self.user_model.objects.get(username=username, enabled=True)

            if u.password == self.encode_password(password, u.salt):
                self.notify(AuthenticationEvent(success=True, username=username))
                return True

        except DoesNotExist:
            self.notify(AuthenticationEvent(success=False, username=username))
            return False

    def create(self, username, password, **kwargs):
        salt = self.generate_salt()
        u = self.user_model(username=username, password=self.encode_password(password, salt), salt=salt, **kwargs)
        u.save()
        self.notify(UserCreatedEvent(user=u))
        return u

    def updatePassword(self, user, password):
        user.salt = self.generate_salt()
        user.password = self.encode_password(password, user.salt)
        user.save()
        self.notify(UserUpdatedEvent(user=user))

    def update(self, user):
        user.save()
        self.notify(UserUpdatedEvent(user=user))

    def find(self, user_id):
        return self.user_model.objects.get(user_id)

    def find_by(self, **kwars):
        return self.user_model.objects(**kwars).first()

    def remove(self, user):
        user.remove()
        self.notify(UserRemovedEvent(user=user))

    def enable(self, user, status):
        user.enabled = status
        user.save()
        self.notify(UserUpdatedEvent(user=user))

    def grant(self, role, resource, permission):
        p = self.permission_model(role=role, resource=resource, permission=permission)
        p.save()
        self.notify(GrantEvent(role=role, resource=resource, permission=permission))

    def revoke(self, role, resource, permission):
        for p in self.permission_model.objects(role=role, resource=resource, permission=permission):
            p.remove()
            self.notify(RevokeEvent(role=role, resource=resource, permission=permission))

    def is_granted(self, role, resource, permission):
        return self.permission_model.objects(role=role, resource=resource, permission=permission).count() > 0

    def role_permissions(self, role):
        return [{"resource": p.resource, "permission": p.permission} for p in self.permission_model.objects(role=role)]

    def resource_permissions(self, resource):
        return [{"resource": p.resource, "permission": p.permission} for p in self.permission_model.objects(resource=resource)]

    def notify(self, event):
        logging.debug(event)
