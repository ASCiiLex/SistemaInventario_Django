from django.db import models


class SlowRequest(models.Model):
    trace_id = models.CharField(max_length=100, db_index=True)

    endpoint = models.CharField(max_length=255, db_index=True)
    method = models.CharField(max_length=10)
    status = models.IntegerField()

    total_time = models.FloatField(db_index=True)
    db_time = models.FloatField()
    db_queries = models.IntegerField()
    slow_queries = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-total_time"]
        indexes = [
            models.Index(fields=["endpoint", "created_at"]),
        ]

    def __str__(self):
        return f"{self.endpoint} ({self.total_time}s)"