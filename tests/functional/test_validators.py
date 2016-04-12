#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.test import TestCase
from microbot.validators import validate_telegram_keyboard
from django.core.exceptions import ValidationError

class TestValidateTelegramKeyboard(TestCase):
    
    def test_valid_no_template(self):
        keyboard_template = "[['a','b']]"
        validate_telegram_keyboard(keyboard_template)
        
    def test_not_valid_no_template(self):
        keyboard_template = "[['a','b']"
        self.assertRaises(ValidationError, validate_telegram_keyboard, keyboard_template)
        
    def test_valid_with_template_inside(self):
        keyboard_template = "[['{{response.value}}','{% if pattern.condition %}{{ pattern.condition }}{% else %}back{% endif %}']]"
        validate_telegram_keyboard(keyboard_template)
        
    def test_not_valid_with_template_inside(self):
        keyboard_template = "[['{{response.value}}','{% if pattern.condition %}{{ pattern.condition }}{% else %}back{% endif %}']"
        self.assertRaises(ValidationError, validate_telegram_keyboard, keyboard_template)
        
    def test_valid_with_template_outside(self):
        keyboard_template = "{% if response.status == 400 %}[['a','b']]{% else %}[['b', 'c']]{% endif %}"
        validate_telegram_keyboard(keyboard_template)
        
    def test_not_valid_with_template_outside(self):
        keyboard_template = "{% if response.status == 400 %}[['a','b']]{% else %}[['b', 'c']{% endif %}"
        self.assertRaises(ValidationError, validate_telegram_keyboard, keyboard_template)
    
    def test_valid_with_template_outside_rendered_as_none(self):
        keyboard_template = "{% if response.status == 200 %}[['Repos', 'Starred'],['Back']]{% endif %}"
        validate_telegram_keyboard(keyboard_template)
    
#     #TODO: this case is not covered. When rendering the bad pattern is not validated
#     def test_not_valid_with_template_outside_not_generated(self):
#         keyboard_template = "{% if response.status == 400 %}[['a','b']{% else %}[['b', 'c']]{% endif %}"
#         self.assertRaises(ValidationError, validate_telegram_keyboard, keyboard_template)    