from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField
from wtforms.validators import Required, Length, Email, Regexp
from wtforms import ValidationError
from flask.ext.pagedown.fields import PageDownField


class StockIdForm(Form):
    stock_id = StringField('What is stock id?', validators=[Required()])
    submit = SubmitField('Submit')


