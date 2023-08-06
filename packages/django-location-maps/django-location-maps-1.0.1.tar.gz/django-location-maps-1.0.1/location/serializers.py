# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from rest_framework import serializers
from .models import Country, State


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = (
            'pk',
            'code2',
            'code3',
            'name'
        )


class StateSerializer(serializers.ModelSerializer):
    country = CountrySerializer(many=False)

    class Meta:
        model = State
        fields = (
            'pk',
            'code',
            'country',
            'name'
        )


class CitySerializer(serializers.ModelSerializer):
    state = StateSerializer(many=False)

    class Meta:
        model = State
        fields = (
            'pk',
            'state',
            'name'
        )
