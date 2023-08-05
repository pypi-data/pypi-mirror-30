#!/usr/bin/env python
# coding: utf-8

"""
    django-reversion-compare unittests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    I used the setup from reversion_compare_test_project !

    TODO:
        * models.OneToOneField()
        * models.IntegerField()

    :copyleft: 2012-2016 by the django-reversion-compare team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function

from reversion import create_revision
from reversion import is_registered
from reversion.models import Revision, Version

try:
    import django_tools
except ImportError as err:
    msg = (
        "Please install django-tools for unittests"
        " - https://github.com/jedie/django-tools/"
        " - Original error: %s"
    ) % err
    raise ImportError(msg)


from .models import Factory, Car
from .utils.test_cases import BaseTestCase
from .utils.fixtures import Fixtures


class FactoryCarModelTest(BaseTestCase):
    """
    unittests that used:
        reversion_compare_test_app.models.Factory
        reversion_compare_test_app.models.Car

    Factory & Car would be registered only in admin.py
    so no relation data would be stored
    """
    def setUp(self):
        super(FactoryCarModelTest, self).setUp()

        fixtures = Fixtures(verbose=False)
        # fixtures = Fixtures(verbose=True)
        self.car = fixtures.create_FactoryCar_data()

        queryset = Version.objects.get_for_object(self.car)
        self.version_ids = queryset.values_list("pk", flat=True)

    def test_initial_state(self):
        self.assertTrue(is_registered(Factory))
        self.assertTrue(is_registered(Car))

        self.assertEqual(Revision.objects.all().count(), 3)
        self.assertEqual(len(self.version_ids), 3)
        self.assertEqual(Version.objects.all().count(), 17)

    def test_select_compare(self):
        response = self.client.get("/admin/reversion_compare_tests/car/%s/history/" % self.car.pk)
        # debug_response(response) # from django-tools
        self.assertContainsHtml(
            response,
            '<input type="submit" value="compare">',
            '<input type="radio" name="version_id1" value="%i" style="visibility:hidden" />' % self.version_ids[0],
            '<input type="radio" name="version_id2" value="%i" checked="checked" />' % self.version_ids[0],
            '<input type="radio" name="version_id1" value="%i" checked="checked" />' % self.version_ids[1],
            '<input type="radio" name="version_id2" value="%i" />' % self.version_ids[1],
            '<input type="radio" name="version_id2" value="%i" />' % self.version_ids[2],
            '<input type="radio" name="version_id2" value="%i" />' % self.version_ids[2],
        )

    def test_diff1(self):
        response = self.client.get(
            "/admin/reversion_compare_tests/car/%s/history/compare/" % self.car.pk,
            data={"version_id2": self.version_ids[1], "version_id1": self.version_ids[2]}
        )
        # debug_response(response) # from django-tools
        self.assertContainsHtml(
            response,
            '<h3>manufacturer<sup class="follow">*</sup></h3>',
            '<h3>supplier<sup class="follow">*</sup></h3>',
            '''
            <p class="highlight">
                <del>- would be deleted supplier</del><br />
                <del>- would be removed supplier</del><br />
                <ins>+ new, would be renamed supplier</ins><br />
                always the same supplier<sup class="follow">*</sup><br />
            </p>
            ''',
            '<h4 class="follow">Note:</h4>',  # info for non-follow related informations
            '<blockquote>version 2: change ForeignKey and ManyToManyField.</blockquote>',
        )

    def test_diff2(self):
        response = self.client.get(
            "/admin/reversion_compare_tests/car/%s/history/compare/" % self.car.pk,
            data={"version_id2": self.version_ids[0], "version_id1":self.version_ids[1]}
        )
        # debug_response(response) # from django-tools
        self.assertContainsHtml(
            response,
            "<del>- motor-car one</del>",
            "<ins>+ motor-car II</ins>",

            '<h3>manufacturer<sup class="follow">*</sup></h3>',
            '<h3>supplier<sup class="follow">*</sup></h3>',
            '''
            <p class="highlight">
                <del>new, would be renamed supplier</del> &rarr; <ins>not new anymore supplier</ins><br />
                always the same supplier<sup class="follow">*</sup><br />
            </p>
            ''',
            '<h4 class="follow">Note:</h4>',  # info for non-follow related informations
            '<blockquote>version 3: change CharField, ForeignKey and ManyToManyField.</blockquote>',
        )


class FactoryCarModelTest2(BaseTestCase):
    """
    unittests that used:
        reversion_compare_test_app.models.Factory
        reversion_compare_test_app.models.Car

    Factory & Car would be registered only in admin.py
    so no relation data would be stored
    """

    def test_initial_state(self):
        self.assertTrue(is_registered(Factory))
        self.assertTrue(is_registered(Car))

        self.assertEqual(Factory.objects.all().count(), 0)
        self.assertEqual(Car.objects.all().count(), 0)

        self.assertEqual(Revision.objects.all().count(), 0)
        self.assertEqual(Version.objects.all().count(), 0)

    def test_deleted_objects(self):
        """
        for:
        https://github.com/jedie/django-reversion-compare/commit/ba22008130f4c16a32eeb900381c2d82ca6fdd9e
        https://travis-ci.org/jedie/django-reversion-compare/builds/72317520
        """
        with create_revision():
            factory1 = Factory.objects.create(name="factory one", address="1 Fake Plaza")
            car = Car.objects.create(
                name="car",
                manufacturer=factory1
            )

        with create_revision():
            factory2 = Factory.objects.create(name="factory two", address="1 Fake Plaza")
            car.manufacturer = factory2
            car.save()

        with create_revision():
            factory1.delete()

        queryset = Version.objects.get_for_object(car)
        version_ids = queryset.values_list("pk", flat=True)  # [3, 2]
        # print("\n", version_ids)

        # response = self.client.get("/admin/reversion_compare_tests/car/%s/history/" % car.pk)
        # debug_response(response) # from django-tools
        self.client.get(
            "/admin/reversion_compare_tests/car/%s/history/compare/" % car.pk,
            data={"version_id2": version_ids[0], "version_id1": version_ids[1]}
        )
        # debug_response(response) # from django-tools



class FactoryCarModelTest3(BaseTestCase):
    """
    unittests that used:
        reversion_compare_test_app.models.Factory
        reversion_compare_test_app.models.Car

    Factory & Car would be registered only in admin.py
    so no relation data would be stored
    """
    def setUp(self):
        super(FactoryCarModelTest3, self).setUp()

        fixtures = Fixtures(verbose=False)
        # fixtures = Fixtures(verbose=True)
        self.car = fixtures.create_FactoryCar_fk_change_data()

        queryset = Version.objects.get_for_object(self.car).order_by('pk')
        self.version_ids = queryset.values_list("pk", flat=True)

    def test_initial_state(self):
        self.assertTrue(is_registered(Factory))
        self.assertTrue(is_registered(Car))

        self.assertEqual(Revision.objects.all().count(), 3)
        self.assertEqual(len(self.version_ids), 3)
        self.assertEqual(Version.objects.all().count(), 9)

    def ftest_diff1(self):
        response = self.client.get(
            "/admin/reversion_compare_tests/car/%s/history/compare/" % self.car.pk,
            data={"version_id2": self.version_ids[0], "version_id1": self.version_ids[1]}
        )
        # debug_response(response) # from django-tools
        self.assertContainsHtml(
            response,
            '<h3>manufacturer<sup class="follow">*</sup></h3>',
            '<p><pre class="highlight">factory I</pre></p>',
        )

    def test_diff1_fk_as_id(self):
        with self.settings(REVERSION_COMPARE_FOREIGN_OBJECTS_AS_ID=True):
            response = self.client.get(
                "/admin/reversion_compare_tests/car/%s/history/compare/" % self.car.pk,
                data={"version_id2": self.version_ids[0], "version_id1": self.version_ids[1]}
            )
            # debug_response(response) # from django-tools
            self.assertNotContainsHtml(
                response,
                '<h3>manufacturer<sup class="follow">*</sup></h3>',
                '<p><pre class="highlight">factory I</pre></p>',
            )

    def test_diff2(self):
        response = self.client.get(
            "/admin/reversion_compare_tests/car/%s/history/compare/" % self.car.pk,
            data={"version_id2": self.version_ids[1], "version_id1": self.version_ids[2]}
        )
        # debug_response(response) # from django-tools
        self.assertContainsHtml(
            response,
            '<del>- factory I</del>',
            '<ins>+ factory two</ins>',
        )

    def test_diff2_fk_as_id(self):
        with self.settings(REVERSION_COMPARE_FOREIGN_OBJECTS_AS_ID=True):
            response = self.client.get(
                "/admin/reversion_compare_tests/car/%s/history/compare/" % self.car.pk,
                data={"version_id2": self.version_ids[1], "version_id1": self.version_ids[2]}
            )
        # debug_response(response) # from django-tools
        self.assertContainsHtml(
            response,
            '<del>- factory I</del>',
            '<ins>+ factory two</ins>',
        )
