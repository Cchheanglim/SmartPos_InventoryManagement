from app.repositories.staff.task_repository import TaskRepository


class TaskService:
    """
    Owns task assignment rules: only the person a task is assigned to
    (or someone with manage_users) can mark it complete — a Cashier
    shouldn't be able to complete another Cashier's task.
    """

    def __init__(self):
        self.task_repo = TaskRepository()

    def assign_task(self, title, description, assigned_to, assigned_by):
        if not title or not title.strip():
            raise ValueError("Task title is required.")
        task_id = self.task_repo.create(title.strip(), (description or "").strip() or None, assigned_to, assigned_by)

        # Imported here (not at module level) to avoid a circular import —
        # notification_service depends on auth_service.
        from app.services.notifications.notification_service import NotificationService
        NotificationService().notify_user(
            assigned_to, f'New task assigned: "{title.strip()}"', category="task",
        )
        return task_id

    def complete_task(self, task_id, completing_user, can_manage_users):
        task = self.task_repo.find_by_id(task_id)
        if task is None:
            raise ValueError("Task not found.")
        if task.assigned_to != completing_user.id and not can_manage_users:
            raise ValueError("You can only complete tasks assigned to you.")
        if task.is_completed:
            raise ValueError("This task is already completed.")
        self.task_repo.mark_complete(task_id)

    def delete_task(self, task_id):
        self.task_repo.delete(task_id)

    def all_tasks(self):
        return self.task_repo.list_all()

    def tasks_for_user(self, user_id):
        return self.task_repo.list_for_user(user_id)

    def pending_count_for_user(self, user_id):
        return self.task_repo.count_pending_for_user(user_id)
