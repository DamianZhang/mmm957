from django import template

register = template.Library()

#要{% load dashboard_extras %}前端才能使用，使用方法: {{ money|函式名稱:"參數" }}
@register.filter(name='money_split')
def money_split(value):
    return str(value)[:len(str(value))-4] + '萬'