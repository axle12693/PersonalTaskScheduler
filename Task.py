class Task:
    def __init__(self, task_id, category_id, task_text,
                 due_date, interval, importance, postpone, allow_early_completion,
                 category_importance):

        self.id = task_id
        self.category_id = category_id
        self.task_text = task_text
        self.due_date = due_date
        self.interval = interval
        self.importance = importance
        self.postpone = postpone
        self.allow_early_completion = allow_early_completion
        self.category_importance = category_importance
