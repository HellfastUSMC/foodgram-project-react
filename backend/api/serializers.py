from rest_framework import serializers
from django.contrib.auth import get_user_model

from food.models import Tag


user = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователей."""

    full_name = serializers.SerializerMethodField('get_full_name')

    def get_full_name(self, obj):
        return obj.get_full_name()

    class Meta:
        model = user
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""

    def get_full_name(self, obj):
        return obj.get_full_name()

    class Meta:
        model = Tag
        fields = '__all__'