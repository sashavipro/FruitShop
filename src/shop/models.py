"""src/shop/models.py."""

from django.db import models


class Product(models.Model):
    """Model representing a fruit available in the warehouse.

    Tracks the current stock quantity, fixed buy/sell prices,
    and caches a string describing the last performed operation.
    """

    name = models.CharField(max_length=50, unique=True)
    stock_quantity = models.IntegerField(default=0)
    buy_price = models.DecimalField(max_digits=8, decimal_places=2)
    sell_price = models.DecimalField(max_digits=8, decimal_places=2)
    last_operation_info = models.CharField(max_length=255, default="", blank=True)

    def __str__(self):
        """Return a string representation of the product."""
        return f"{self.name} (В наличии: {self.stock_quantity})"  # noqa: RUF001


class BankAccount(models.Model):
    """Model representing the company's global bank account.

    Stores the total balance used for buying and updated after selling products.
    Expected to contain only a single record in the database.
    """

    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        """Return a string representation of the bank account balance."""
        return f"Баланс: {self.balance} USD"


class TradeLog(models.Model):
    """Model for logging the results of trading operations.

    Records the timestamp, status (success or error), and a detailed message
    for every background task attempting to buy or sell products.
    """

    class Status(models.TextChoices):
        """Available statuses for a trade operation."""

        SUCCESS = "SUCCESS", "Success"
        ERROR = "ERROR", "Error"

    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=Status.choices)
    message = models.TextField()

    class Meta:
        """Meta options for the TradeLog model."""

        ordering = ["-created_at"]

    def __str__(self):
        """Return a string representation of the trade log."""
        time_str = self.created_at.strftime("%d.%m.%Y %H:%M")
        return f"[{self.status}] {time_str} - {self.message[:30]}..."


class TaskRegistry(models.Model):
    """Model to track the execution status and timestamps of background tasks.

    Used to prevent concurrent executions of specific tasks and to provide
    the frontend with the latest run times for periodic polling.
    """

    class Status(models.TextChoices):
        """Available statuses for a background task."""

        IDLE = "idle", "Idle"
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    task_name = models.CharField(max_length=100, unique=True)
    last_run_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.IDLE,
    )

    def __str__(self):
        """Return a string representation of the task registry entry."""
        return f"Таска: {self.task_name} | Статус: {self.status}"


class Declaration(models.Model):
    """Model representing uploaded declaration documents.

    Stores the file path and the exact upload timestamp.
    """

    file = models.FileField(upload_to="declarations/%Y/%m/%d/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return a string representation of the declaration."""
        return f"Декларация от {self.uploaded_at.strftime('%d.%m.%Y')}"
