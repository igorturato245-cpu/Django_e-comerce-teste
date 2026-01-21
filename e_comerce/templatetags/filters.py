from django.template import Library
from django import template
from utils import utils

register=template.Library()

@register.filter
def formata_preco(preco):
    return utils.formata_preco(preco)