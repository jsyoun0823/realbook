from mybook.models import UserProfile
from rest_framework import serializers


class UsersSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = UserProfile
        fields = ('name')
