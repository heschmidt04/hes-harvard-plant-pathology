from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


# Also used for password updates
class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    verify = PasswordField('Verify Password', validators=[DataRequired()])
    submit = SubmitField('Signup')

# User Login
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# Note: must add to app.py to make sure the image is not too big 
# app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024  # 4MB max-limit. 

class ImageUploadForm(FlaskForm):
    #username = StringField(label="Username", render_kw={'readonly': True})
    image = FileField(label='Image', validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Images only!')])
    submit = SubmitField('Submit')