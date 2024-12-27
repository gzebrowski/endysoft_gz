from rest_framework import serializers


class BaseTenantSerializer(serializers.ModelSerializer):
    def save(self, **kwargs):
        if 'tenant_id' not in kwargs:
            kwargs['tenant_id'] = self.context["request"].tenant_id
        return super().save(**kwargs)

    def create(self, validated_data):
        validated_data['tenant_id'] = self.context["request"].tenant_id
        return super().create(validated_data)
