# Copyright (C) 2012-2015 Xue Can <xuecan@gmail.com> and contributors.
# Licensed under the MIT license: http://opensource.org/licenses/mit-license

"""
# Shortcuts of Flask-WTF and WTForms

Requirement:

* Flask-WTF
"""

# work with Flask-WTF 0.9.3 and WTForms 1.0.5

__all__ = ['Form', 'field', 'validator', 'ValidationError', 'StopValidation']


from flask_wtf import Form, RecaptchaField
import flask_wtf.recaptcha.fields
import wtforms.fields.core
import wtforms.fields.simple
import wtforms.fields.html5
import wtforms.validators


class fields:
    """fields from WTForms and Flask-WTF"""
    boolean = wtforms.fields.core.BooleanField
    decimal = wtforms.fields.html5.DecimalField
    decimal_range = wtforms.fields.html5.DecimalRangeField
    date = wtforms.fields.html5.DateField
    datetime = wtforms.fields.html5.DateTimeField
    datetime_local = wtforms.fields.html5.DateTimeLocalField
    email = wtforms.fields.html5.EmailField
    field_list = wtforms.fields.core.FieldList
    file_ = wtforms.fields.simple.FileField
    float_ = wtforms.fields.core.FloatField
    form = wtforms.fields.core.FormField
    hidden = wtforms.fields.simple.HiddenField
    integer = wtforms.fields.html5.IntegerField
    integer_range = wtforms.fields.html5.IntegerRangeField
    password = wtforms.fields.simple.PasswordField
    radio = wtforms.fields.core.RadioField
    recaptcha = flask_wtf.recaptcha.fields.RecaptchaField
    search = wtforms.fields.html5.SearchField
    select = wtforms.fields.core.SelectField
    select_multiple = wtforms.fields.core.SelectMultipleField
    string = wtforms.fields.core.StringField
    submit = wtforms.fields.simple.SubmitField
    tel = wtforms.fields.html5.TelField
    textarea = wtforms.fields.simple.TextAreaField
    url = wtforms.fields.html5.URLField


class validators:
    """validators form WTForms"""
    email = wtforms.validators.Email
    equal_to = wtforms.validators.EqualTo
    ip_address = wtforms.validators.IPAddress
    mac_address = wtforms.validators.MacAddress
    length = wtforms.validators.Length
    number_range = wtforms.validators.NumberRange
    optional = wtforms.validators.Optional
    required = wtforms.validators.Required
    input_required = wtforms.validators.InputRequired
    data_required = wtforms.validators.DataRequired
    regexp = wtforms.validators.Regexp
    url = wtforms.validators.URL
    any_of = wtforms.validators.AnyOf
    none_of = wtforms.validators.NoneOf


ValidationError = wtforms.validators.ValidationError
StopValidation = wtforms.validators.StopValidation


# ----------------------------------------------------------------------
# patch for wtforms.widgets.html_params
# ----------------------------------------------------------------------
from cgi import escape
from wtforms.compat import text_type, iteritems
import wtforms.widgets
import wtforms.widgets.core


def html_params(**kwargs):
    """
    Generate HTML parameters from inputted keyword arguments.
    """
    params = []
    for k, v in sorted(iteritems(kwargs)):
        if k.endswith('_'):
            k = k[:-1]
        elif k.endswith('__'):
            k = k[:-2]
        else:
            k = k.replace('_', '-')  # PATCH HERE: data_custom => data-custom
        if v is True:
            params.append(k)
        else:
            params.append('%s="%s"' % (text_type(k), escape(text_type(v),
                                                            quote=True)))
    return ' '.join(params)

wtforms.widgets.html_params = html_params
wtforms.widgets.core.html_params = html_params
