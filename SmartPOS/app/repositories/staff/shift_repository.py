from app.extensions import get_db
from app.models.staff.shift import ShiftTemplate
from app.repositories.base_repository import BaseRepository


class ShiftRepository(BaseRepository):
    table_name = "shift_templates"
    model_class = ShiftTemplate

    def create(self, name, start_time, end_time):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                "INSERT INTO shift_templates (name, start_time, end_time) VALUES (%s, %s, %s)",
                (name, start_time, end_time),
            )
            new_id = cur.lastrowid
        db.commit()
        return new_id

    def update(self, shift_id, name, start_time, end_time):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                "UPDATE shift_templates SET name = %s, start_time = %s, end_time = %s WHERE id = %s",
                (name, start_time, end_time, shift_id),
            )
        db.commit()
