# Copyright (C) 2012-2017 Xue Can <xuecan@gmail.com> and contributors.
# Licensed under the MIT license: http://opensource.org/licenses/mit-license

"""
# Shortcuts of Flask-WTF and WTForms

Requirement:

* Flask-WTF
"""

# work with Flask-WTF 0.14.2 and WTForms 2.1

from flask_wtf import FlaskForm as Form
import flask_wtf.file
from wtforms import fields, validators
from flask_wtf.csrf import CSRFError
from html import escape
from wtforms.compat import text_type, iteritems
import wtforms.widgets.core


__all__ = ["Form", "field", "validator",
           "ValidationError", "StopValidation", "CSRFError"]


class Field(object):

    def __init__(self):
        # from wtforms: Basic fields
        # http://wtforms.readthedocs.io/en/latest/fields.html#basic-fields
        self.boolean = fields.BooleanField
        self.date = fields.DateField
        self.datetime = fields.DateTimeField
        self.decimal = fields.DecimalField
        self.float = fields.FloatField
        self.integer = fields.IntegerField
        self.radio = fields.RadioField
        self.select = fields.SelectField
        self.select_multiple = fields.SelectMultipleField
        self.submit = fields.SubmitField
        self.string = fields.StringField
        # from wtforms: Convenience Fields
        # http://wtforms.readthedocs.io/en/latest/fields.html#convenience-fields
        self.hidden = fields.HiddenField
        self.password = fields.PasswordField
        self.textarea = fields.TextAreaField
        # from wtforms: Field Enclosures
        # http://wtforms.readthedocs.io/en/latest/fields.html#field-enclosures
        self.form = fields.FormField
        self.field_list = fields.FieldList
        # from flask_wtf
        # https://flask-wtf.readthedocs.io/en/stable/api.html#module-flask_wtf
        self.recaptcha = flask_wtf.RecaptchaField
        self.file = flask_wtf.file.FileField
        # shortcuts
        self.bool = self.boolean
        self.int = self.integer
        self.str = self.string


field = Field()

class Validator(object):

    def __init__(self):
        # from wtforms
        # http://wtforms.readthedocs.io/en/latest/validators.html#built-in-validators
        self.data_required = validators.DataRequired
        self.email = validators.Email
        self.equal_to = validators.EqualTo
        self.input_required = validators.InputRequired
        self.ip_address = validators.IPAddress
        self.length = validators.Length
        self.mac_address = validators.MacAddress
        self.number_range = validators.NumberRange
        self.optional = validators.Optional
        self.regexp = validators.Regexp
        self.url = validators.URL
        self.any_of = validators.AnyOf
        self.none_of = validators.NoneOf
        # from flask_wtf
        # https://flask-wtf.readthedocs.io/en/stable/api.html#module-flask_wtf
        self.file_allowed = flask_wtf.file.FileAllowed
        self.file_required = flask_wtf.file.FileRequired
        self.recaptcha = flask_wtf.Recaptcha
        # shortcut
        self.required = self.input_required

validator = Validator()

ValidationError = wtforms.validators.ValidationError
StopValidation = wtforms.validators.StopValidation


# ----------------------------------------------------------------------
# patch for wtforms.widgets.core.html_params
# ----------------------------------------------------------------------

def html_params(**kwargs):
    """
    Generate HTML parameters from inputted keyword arguments.
    """
    params = []
    for k, v in sorted(iteritems(kwargs)):
        if k.endswith("_"):
            k = k[:-1]
        elif k.endswith("__"):
            k = k[:-2]
        else:
            k = k.replace("_", "-")  # PATCH HERE: data_custom => data-custom
        if v is True:
            params.append(k)
        elif v is False:
            pass
        else:
            params.append('%s="%s"' % (text_type(k),
                                       escape(text_type(v), quote=True)))
    return " ".join(params)


wtforms.widgets.html_params = html_params
wtforms.widgets.core.html_params = html_params
