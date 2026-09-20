from app.repositories.staff.notification_repository import NotificationRepository
from app.repositories.auth.user_repository import UserRepository


class NotificationService:
    def __init__(self):
        self.notification_repo = NotificationRepository()
        self.user_repo = UserRepository()

    def list_for_user(self, user_id, unread_only=False, limit=50):
        return self.notification_repo.list_for_user(user_id, unread_only, limit)

    def count_unread(self, user_id):
        return self.notification_repo.count_unread(user_id)

    def notify_user(self, user_id, message, category="general"):
        self.notification_repo.create(user_id, message, category)

    def notify_users_with_permission(self, permission_name, message, category="general"):
        """
        Fan a notification out to every active user who currently holds
        `permission_name` (via their role or an individual grant). Used
        for things like low-stock alerts, where "everyone who can manage
        products" is the right audience rather than one specific user.

        Imports AuthService here (not at module level) to avoid a circular
        import — auth_service doesn't depend on this module, but several
        of the services that DO depend on this one (inventory, tasks) are
        also imported by auth-adjacent code at startup.
        """
        from app.services.auth.auth_service import AuthService

        auth_service = AuthService()
        recipient_ids = [
            user.id for user in self.user_repo.list_all()
            if user.is_active and auth_service.has_permission(user, permission_name)
        ]
        if recipient_ids:
            self.notification_repo.create_for_users(recipient_ids, message, category)

    def mark_read(self, notification_id, user_id):
        self.notification_repo.mark_read(notification_id, user_id)

    def mark_all_read(self, user_id):
        self.notification_repo.mark_all_read(user_id)
