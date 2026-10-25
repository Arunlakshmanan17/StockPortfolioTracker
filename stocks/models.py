from django.db import models
from django.contrib.auth.models import User


class StockHolding(models.Model):

    # User who owns this stock
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="stock_holdings"
    )

    # Stock information
    symbol = models.CharField(
        max_length=20
    )

    company_name = models.CharField(
        max_length=100
    )

    # Number of shares
    quantity = models.PositiveIntegerField()

    # Price when user purchased
    purchase_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    # Current market price
    current_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    # Date purchased
    purchase_date = models.DateField(
        auto_now_add=True
    )

    # =========================
    # CALCULATE INVESTMENT
    # =========================

    def investment_value(self):

        return (
            self.quantity *
            self.purchase_price
        )

    # =========================
    # CALCULATE CURRENT VALUE
    # =========================

    def current_value(self):

        return (
            self.quantity *
            self.current_price
        )

    # =========================
    # CALCULATE PROFIT / LOSS
    # =========================

    def profit_loss(self):

        return (
            self.current_value()
            - self.investment_value()
        )

    # =========================
    # DISPLAY STOCK
    # =========================

    def __str__(self):

        return (
            f"{self.symbol} - "
            f"{self.user.username}"
        )