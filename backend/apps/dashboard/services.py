from datetime import timedelta

from django.db.models import Count, Sum
from django.utils import timezone

from apps.charging.models import ChargingPile
from apps.common.constants.enums import OrderStatus, PaymentStatus, PileStatus, VehicleStatus
from apps.orders.models import TripOrder
from apps.vehicles.models import Vehicle


class DashboardService:
    @staticmethod
    def overview() -> dict:
        today = timezone.now().date()
        total_piles = ChargingPile.objects.count() or 1
        used_piles = ChargingPile.objects.filter(status=PileStatus.CHARGING).count()
        in_30_days = today + timedelta(days=30)
        insurance_expired = Vehicle.objects.filter(insurance_expiry__lt=today).count()
        insurance_expiring_30 = Vehicle.objects.filter(insurance_expiry__gte=today, insurance_expiry__lte=in_30_days).count()
        return {
            "vehicles_online": Vehicle.objects.filter(status=VehicleStatus.OPERATING).count(),
            "vehicles_total": Vehicle.objects.count(),
            "today_orders": TripOrder.objects.filter(created_at__date=today).count(),
            "today_revenue": TripOrder.objects.filter(created_at__date=today, payment_status=PaymentStatus.PAID).aggregate(total=Sum("fare"))["total"] or 0,
            "pile_utilization": round(used_piles / total_piles * 100, 2),
            "vehicles_insurance_expired": insurance_expired,
            "vehicles_insurance_expiring_30": insurance_expiring_30,
            "vehicles_pending_renewal": insurance_expired + insurance_expiring_30,
        }

    @staticmethod
    def order_trend() -> list[dict]:
        rows = TripOrder.objects.extra(select={"day": "date(created_at)"}).values("day").annotate(count=Count("id")).order_by("day")[:14]
        return list(rows)

    @staticmethod
    def revenue_stats() -> dict:
        by_type = Vehicle.objects.values("type").annotate(count=Count("id"))
        completed = TripOrder.objects.filter(status=OrderStatus.COMPLETED).aggregate(total=Sum("fare"))["total"] or 0
        return {"total_revenue": completed, "vehicle_distribution": list(by_type)}
