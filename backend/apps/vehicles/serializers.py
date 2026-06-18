from datetime import date

from rest_framework import serializers

from apps.users.serializers import UserSerializer
from apps.vehicles.models import Vehicle


class VehicleSerializer(serializers.ModelSerializer):
    driver_detail = UserSerializer(source="driver", read_only=True)
    insurance_days_remaining = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = "__all__"

    def get_insurance_days_remaining(self, obj: Vehicle) -> int:
        return (obj.insurance_expiry - date.today()).days
