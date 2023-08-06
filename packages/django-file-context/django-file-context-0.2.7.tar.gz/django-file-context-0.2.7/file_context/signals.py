# coding: utf-8
from django.dispatch import Signal


file_attached = Signal(providing_args=['instance', 'file', 'user', 'data'])
file_detached = Signal(providing_args=['instance', 'file', 'user', 'data'])
