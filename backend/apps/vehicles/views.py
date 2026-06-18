from datetime import timedelta

from django.utils import timezone
from rest_framework import decorators, response, status, viewsets

from apps.common.constants.enums import VehicleStatus
from apps.common.permissions import IsOperatorOrAdmin
from apps.maintenance.serializers import MaintenanceRecordSerializer
from apps.vehicles.models import Vehicle
from apps.vehicles.serializers import VehicleSerializer
from apps.vehicles.services import VehicleService


class VehicleViewSet(viewsets.ModelViewSet):
    serializer_class = VehicleSerializer
    permission_classes = [IsOperatorOrAdmin]

    def get_queryset(self):
        queryset = Vehicle.objects.select_related("driver").all()
        user = self.request.user
        if getattr(user, "role", "") == "DRIVER":
            queryset = queryset.filter(driver=user)
        if vehicle_type := self.request.query_params.get("type"):
            queryset = queryset.filter(type=vehicle_type)
        if state := self.request.query_params.get("status"):
            queryset = queryset.filter(status=state)
        today = timezone.now().date()
        if insurance_filter := self.request.query_params.get("insurance_status"):
            if insurance_filter == "expired":
                queryset = queryset.filter(insurance_expiry__lt=today)
            elif insurance_filter == "expiring_7":
                queryset = queryset.filter(insurance_expiry__gte=today, insurance_expiry__lte=today + timedelta(days=7))
            elif insurance_filter == "expiring_30":
                queryset = queryset.filter(insurance_expiry__gte=today, insurance_expiry__lte=today + timedelta(days=30))
            elif insurance_filter == "expiring_90":
                queryset = queryset.filter(insurance_expiry__gte=today, insurance_expiry__lte=today + timedelta(days=90))
        if insurance_days_max := self.request.query_params.get("insurance_days_max"):
            try:
                days = int(insurance_days_max)
                queryset = queryset.filter(insurance_expiry__lte=today + timedelta(days=days))
            except ValueError:
                pass
        return queryset

    def perform_create(self, serializer):
        serializer.save(status=VehicleStatus.PENDING)

    @decorators.action(detail=False, methods=["get"], url_path="locations")
    def locations(self, request):
        qs = self.get_queryset().filter(status=VehicleStatus.OPERATING)
        return response.Response(VehicleSerializer(qs, many=True).data)

    @decorators.action(detail=True, methods=["patch"])
    def approve(self, request, pk=None):
        return response.Response(VehicleSerializer(VehicleService.approve(self.get_object())).data)

    @decorators.action(detail=True, methods=["patch"], url_path="assign-driver")
    def assign_driver(self, request, pk=None):
        return response.Response(VehicleSerializer(VehicleService.assign_driver(self.get_object(), request.data["driver_id"])).data)

    @decorators.action(detail=True, methods=["patch"])
    def maintenance(self, request, pk=None):
        return response.Response(VehicleSerializer(VehicleService.mark_maintenance(self.get_object())).data)

    @decorators.action(detail=True, methods=["patch"])
    def disable(self, request, pk=None):
        return response.Response(VehicleSerializer(VehicleService.disable(self.get_object())).data)

    @decorators.action(detail=True, methods=["get"], url_path="maintenance-records")
    def maintenance_records(self, request, pk=None):
        data = MaintenanceRecordSerializer(self.get_object().maintenance_records.all(), many=True).data
        return response.Response(data, status=status.HTTP_200_OK)
