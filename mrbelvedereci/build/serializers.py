from rest_framework import serializers

from models import Build
from models import Rebuild


class BuildSerializer(serializers.ModelSerializer):

    class Meta:
        depth = 1
        model = Build
        fields = '__all__'


class RebuildSerializer(serializers.ModelSerializer):

    class Meta:
        model = Rebuild
        fields = '__all__'
