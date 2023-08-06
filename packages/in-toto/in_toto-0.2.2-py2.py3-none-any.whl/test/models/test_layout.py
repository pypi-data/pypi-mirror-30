#!/usr/bin/env python
"""
<Program Name>
  test_layout.py

<Author>
  Santiago Torres-Arias <santiago@nyu.edu>

<Started>
  Nov 18, 2016

<Copyright>
  See LICENSE for licensing information.

<Purpose>
  Test layout class functions.

"""

import os
import unittest
import datetime
from in_toto.models.layout import Layout, Step, Inspection
import in_toto.models.link
import in_toto.exceptions
import securesystemslib.exceptions

class TestLayoutValidator(unittest.TestCase):
  """Test verifylib.verify_delete_rule(rule, artifact_queue) """

  def setUp(self):
    """Populate a base layout that we can use."""
    self.layout = Layout()
    self.layout.expires = '2016-11-18T16:44:55Z'

  def test_wrong_type(self):
    """Test that the type field is validated properly."""

    with self.assertRaises(securesystemslib.exceptions.FormatError):
      self.layout._type = "wrong"
      self.layout._validate_type()
      self.layout.validate()

    self.layout._type = "layout"
    self.layout._validate_type()

  def test_wrong_expires(self):
    """Test the expires field is properly populated."""

    self.layout.expires = ''
    with self.assertRaises(securesystemslib.exceptions.FormatError):
      self.layout._validate_expires()

    with self.assertRaises(securesystemslib.exceptions.FormatError):
      self.layout.validate()

    self.layout.expires = '-1'
    with self.assertRaises(securesystemslib.exceptions.FormatError):
      self.layout._validate_expires()

    with self.assertRaises(securesystemslib.exceptions.FormatError):
      self.layout.validate()

    # notice the wrong month
    self.layout.expires = '2016-13-18T16:44:55Z'
    with self.assertRaises(securesystemslib.exceptions.FormatError):
      self.layout._validate_expires()

    with self.assertRaises(securesystemslib.exceptions.FormatError):
      self.layout.validate()

    self.layout.expires = '2016-11-18T16:44:55Z'
    self.layout._validate_expires()
    self.layout.validate()

  def test_wrong_key_dictionary(self):
    """Test that the keys dictionary is properly populated."""
    rsa_key_one = securesystemslib.keys.generate_rsa_key()
    rsa_key_two = securesystemslib.keys.generate_rsa_key()

    # FIXME: attr.ib reutilizes the default dictionary, so future constructor
    # are not empty...
    self.layout.keys = {"kek": rsa_key_one}
    with self.assertRaises(securesystemslib.exceptions.FormatError):
      self.layout._validate_keys()

    with self.assertRaises(securesystemslib.exceptions.FormatError):
      self.layout.validate()

    self.layout.keys = {}
    self.layout.keys[rsa_key_two['keyid']] = "kek"
    with self.assertRaises(securesystemslib.exceptions.FormatError):
      self.layout._validate_keys()

    with self.assertRaises(securesystemslib.exceptions.FormatError):
      self.layout.validate()

    self.layout.keys = {}
    del rsa_key_one["keyval"]["private"]
    del rsa_key_two["keyval"]["private"]
    self.layout.keys[rsa_key_one['keyid']] = rsa_key_one
    self.layout.keys[rsa_key_two['keyid']] = rsa_key_two

    self.layout._validate_keys()
    self.layout.validate()

  def test_wrong_steps_list(self):
    """Check that the validate method checks the steps' correctness."""
    self.layout.steps = "not-a-step"

    with self.assertRaises(securesystemslib.exceptions.FormatError):
      self.layout.validate()

    test_step = Step(name="this-is-a-step")
    with self.assertRaises(securesystemslib.exceptions.FormatError):
      test_step.material_matchrules = ['this is a malformed step']
      self.layout.steps = [test_step]
      self.layout.validate()


    test_step = Step(name="this-is-a-step")
    test_step.material_matchrules = [["CREATE", "foo"]]
    test_step.threshold = 1
    self.layout.steps = [test_step]
    self.layout.validate()

  def test_wrong_inspect_list(self):
    """Check that the validate method checks the inspections' correctness."""

    self.layout.inspect = "not-an-inspection"
    with self.assertRaises(securesystemslib.exceptions.FormatError):
      self.layout.validate()

    test_inspection = Inspection(name="this-is-a-step")
    test_inspection.material_matchrules = ['this is a malformed matchrule']
    self.layout.inspect = [test_inspection]
    with self.assertRaises(securesystemslib.exceptions.FormatError):
      self.layout.validate()

    test_inspection = Inspection(name="this-is-a-step")
    test_inspection.material_matchrules = [["CREATE", "foo"]]
    self.layout.inspect = [test_inspection]
    self.layout.validate()

  def test_repeated_step_names(self):
    """Check that only unique names exist in the steps and inspect lists"""

    self.layout.steps = [Step(name="name"), Step(name="name")]
    with self.assertRaises(securesystemslib.exceptions.FormatError):
      self.layout.validate()

    self.layout.steps = [Step(name="name")]
    self.layout.inspect = [Inspection(name="name")]
    with self.assertRaises(securesystemslib.exceptions.FormatError):
      self.layout.validate()

    self.layout.step = [Step(name="name"), Step(name="othername")]
    self.layout.inspect = [Inspection(name="thirdname")]
    self.layout.validate()

  def test_import_step_metadata_wrong_type(self):
    functionary_key = securesystemslib.keys.generate_rsa_key()
    name = "name"

    # Create and dump a link file with a wrong type
    link_name = in_toto.models.link.FILENAME_FORMAT.format(
        step_name=name, keyid=functionary_key["keyid"])
    link_path = os.path.abspath(link_name)
    link = in_toto.models.link.Link(name=name)
    link._type = "wrong-type"
    link.dump(link_path)

    # Add the single step to the test layout and try to read the failing link
    self.layout.steps.append(Step(
        name=name, pubkeys=[functionary_key["keyid"]]))

    with self.assertRaises(in_toto.exceptions.LinkNotFoundError):
      self.layout.import_step_metadata_from_files_as_dict()

    # Clean up
    os.remove(link_path)

if __name__ == "__main__":
  unittest.main()
