from rest_framework import serializers

from models import Build


class BuildSerializer(serializers.ModelSerializer):

    class Meta:
        depth = 1
        model = Build
        fields = '__all__'
