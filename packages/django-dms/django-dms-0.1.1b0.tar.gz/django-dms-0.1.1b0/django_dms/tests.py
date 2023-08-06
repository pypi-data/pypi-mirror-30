from django.test import TestCase
from django.template import Context, Template


class DMSTestCase(TestCase):
    def render_template(self, string, context=None):
        context = context or {}
        context = Context(context)
        return Template(string).render(context)

    def test_positive_longitude(self):
        rendered = self.render_template(
            '{% load dms %}'
            '{{ 2.3508|longitude }}'
        )
        self.assertEqual(rendered, u'2\u00b0 21&#39; 03&quot; E')

    def test_negative_longitude(self):
        rendered = self.render_template(
            '{% load dms %}'
            '{{ -77.0089|longitude }}'
        )
        self.assertEqual(rendered, u'77\u00b0 00&#39; 32&quot; W')

    def test_positive_latitude(self):
        rendered = self.render_template(
            '{% load dms %}'
            '{{ 38.8897|latitude }}'
        )
        self.assertEqual(rendered, u'38\u00b0 53&#39; 23&quot; N')

    def test_negative_latitude(self):
        rendered = self.render_template(
            '{% load dms %}'
            '{{ -26.204444|latitude }}'
        )
        self.assertEqual(rendered, u'26\u00b0 12&#39; 16&quot; S')

    def test_value_with_zero_seconds(self):
        rendered = self.render_template(
            '{% load dms %}'
            '{{ 21.433333|longitude }}'
        )
        self.assertEqual(rendered, u'21\u00b0 26&#39; 00&quot; E')

    def test_value_with_zero_minutes_and_zero_seconds(self):
        rendered = self.render_template(
            '{% load dms %}'
            '{{ 42|latitude }}'
        )
        self.assertEqual(rendered, u'42\u00b0 00&#39; 00&quot; N')

    def test_non_valid_longitude(self):
        rendered = self.render_template(
            '{% load dms %}'
            '{{ 185|latitude }}'
        )
        self.assertEqual(rendered, '185')
        
    def test_non_valid_latitude(self):
        rendered = self.render_template(
            '{% load dms %}'
            '{{ -91|latitude }}'
        )
        self.assertEqual(rendered, '-91')

    def test_value_not_a_number(self):
        rendered = self.render_template(
            '{% load dms %}'
            '{{ "abc"|latitude }}'
        )
        self.assertEqual(rendered, 'abc')
