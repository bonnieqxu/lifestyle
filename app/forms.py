from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SelectField, DateField, TextAreaField, TimeField
from wtforms import BooleanField, validators, RadioField, SubmitField, DecimalField
from wtforms.validators import DataRequired, Length, EqualTo, Email, InputRequired, NumberRange
from flask_wtf.file import MultipleFileField, FileAllowed
from datetime import date

#create flaskform for add member form
#additional field user status
class AddMemberForm(FlaskForm):
    username = StringField(label='Username', validators=[DataRequired(),Length(min=3,max=20)])
    password = PasswordField(label='Password',validators=[DataRequired(),Length(min=8,max=12)])
    confirm_password = PasswordField(label='Confirm Password',validators=[DataRequired(),EqualTo('password')])
    choices = [('Mr', 'Mr'), ('Mrs', 'Mrs'), ('Ms', 'Ms'), ('Dr', 'Dr')]
    title = SelectField(label='Title', choices=choices)
    firstname = StringField(label='First Name', validators=[DataRequired(),Length(min=3,max=20)])
    lastname = StringField(label='Family Name', validators=[DataRequired(),Length(min=3,max=20)])
    position = StringField(label='Position')
    email = EmailField(label='Email',validators=[DataRequired(),Email()])
    address = StringField(label='Address')
    phone = StringField(label='Phone')
    dob = DateField(label='Date of Birth')

#create flaskform for edit member form
#additional field user status
class EditMemberForm(FlaskForm):
    choices = [('Mr', 'Mr'), ('Mrs', 'Mrs'), ('Ms', 'Ms'), ('Dr', 'Dr')]
    title = SelectField(label='Title', choices=choices)
    firstname = StringField(label='First Name', validators=[DataRequired(),Length(min=3,max=20)])
    lastname = StringField(label='Family Name', validators=[DataRequired(),Length(min=3,max=20)])
    position = StringField(label='Position')
    email = EmailField(label='Email',validators=[DataRequired(),Email()])
    address = StringField(label='Address')
    phone = StringField(label='Phone')
    dob = DateField(label='Date of Birth')
    choices = [('A', 'Active'), ('I', 'Inactive')]
    status = SelectField(label='Status', choices=choices)
    images = MultipleFileField('Image File', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!'),
        validators.Length(max=1, message='You can upload up to 1 image only.')
    ])

    #create flaskform for edit member form
#additional field user status
class EditMemberProfileForm(FlaskForm):
    choices = [('Mr', 'Mr'), ('Mrs', 'Mrs'), ('Ms', 'Ms'), ('Dr', 'Dr')]
    title = SelectField(label='Title', choices=choices)
    firstname = StringField(label='First Name', validators=[DataRequired(),Length(min=3,max=20)])
    lastname = StringField(label='Family Name', validators=[DataRequired(),Length(min=3,max=20)])
    position = StringField(label='Position')
    email = EmailField(label='Email',validators=[DataRequired(),Email()])
    address = StringField(label='Address')
    phone = StringField(label='Phone')
    dob = DateField(label='Date of Birth')
    images = MultipleFileField('Image File', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!'),
        validators.Length(max=1, message='You can upload up to 1 image only.')
    ])
#create flaskform for add tutor form
#additional field user status
class AddTutorForm(FlaskForm):
    username = StringField(label='Username', validators=[DataRequired(),Length(min=3,max=20)])
    password = PasswordField(label='Password',validators=[DataRequired(),Length(min=8,max=12)])
    confirm_password = PasswordField(label='Confirm Password',validators=[DataRequired(),EqualTo('password')])
    choices = [('Mr', 'Mr'), ('Mrs', 'Mrs'), ('Ms', 'Ms'), ('Dr', 'Dr')]
    title = SelectField(label='Title', choices=choices)
    firstname = StringField(label='First Name', validators=[DataRequired(),Length(min=3,max=20)])
    lastname = StringField(label='Family Name', validators=[DataRequired(),Length(min=3,max=20)])
    position = StringField(label='Position')
    phone = StringField(label='Phone No.')
    email = EmailField(label='Email',validators=[DataRequired(),Email()])
    profile = TextAreaField(label='Profile', render_kw={"rows": 6})
    images = MultipleFileField('Image File', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!'),
        validators.Length(max=1, message='You can upload up to 1 image only.')
    ])


#create flaskform for edit tutor form
#additional field user status
class EditTutorForm(FlaskForm):
    choices = [('Mr', 'Mr'), ('Mrs', 'Mrs'), ('Ms', 'Ms'), ('Dr', 'Dr')]
    title = SelectField(label='Title', choices=choices)
    firstname = StringField(label='First Name', validators=[DataRequired(),Length(min=3,max=20)])
    lastname = StringField(label='Family Name', validators=[DataRequired(),Length(min=3,max=20)])
    position = StringField(label='Position')
    phone = StringField(label='Phone No.')
    email = EmailField(label='Email',validators=[DataRequired(),Email()])
    profile = TextAreaField(label='Profile', render_kw={"rows": 6})
    images = MultipleFileField('Image File', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!'),
        validators.Length(max=1, message='You can upload up to 1 image only.')
    ])
    choices = [('A', 'Active'), ('I', 'Inactive')]
    status = SelectField(label='Status', choices=choices)

    #create flaskform for edit tutor form
#additional field user status
class EditTutorProfileForm(FlaskForm):
    choices = [('Mr', 'Mr'), ('Mrs', 'Mrs'), ('Ms', 'Ms'), ('Dr', 'Dr')]
    title = SelectField(label='Title', choices=choices)
    firstname = StringField(label='First Name', validators=[DataRequired(),Length(min=3,max=20)])
    lastname = StringField(label='Family Name', validators=[DataRequired(),Length(min=3,max=20)])
    position = StringField(label='Position')
    phone = StringField(label='Phone No.')
    email = EmailField(label='Email',validators=[DataRequired(),Email()])
    profile = TextAreaField(label='Profile', render_kw={"rows": 6})
    images = MultipleFileField('Image File', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!'),
        validators.Length(max=1, message='You can upload up to 1 image only.')
    ])

#create flaskform for add workshop type form
class AddWorkshopTypeForm(FlaskForm):
    workshoptype = StringField(label='Workshop Type', validators=[DataRequired(),Length(min=3,max=100)])
    workshopdesc = TextAreaField(label='Workshop Common Description', render_kw={"rows": 10})

class AddLessonTypeForm(FlaskForm):
    lessontype = StringField(label='Lesson Type', validators=[DataRequired(),Length(min=3,max=100)])
    lessondesc = TextAreaField(label='Lesson Common Description', render_kw={"rows": 10})

class AddLocationForm(FlaskForm):
    locationname = StringField(label='Name', validators=[DataRequired(),Length(min=3,max=100)])
    locationdesc = TextAreaField(label='Description', render_kw={"rows": 10})
    locationmap = MultipleFileField('Image File', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!'),
        validators.Length(max=1, message='You can upload up to 1 location map only.')
    ])
    choices = [('1', '1'), ('50', '50'), ('100', '100'), ('150', '150'), ('200', '200'), ('250', '250')]
    locationlimit = SelectField(label='Limit', coerce=int, choices=choices)

class EditLocationForm(FlaskForm):
    locationname = StringField(label='Name', validators=[DataRequired(),Length(min=3,max=100)])
    locationdesc = TextAreaField(label='Description', render_kw={"rows": 10})
    locationmap = MultipleFileField('Image File', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!'),
        validators.Length(max=1, message='You can upload up to 1 location map only.')
    ])
    choices = [('1', '1'), ('50', '50'), ('100', '100'), ('150', '150'), ('200', '200'), ('250', '250')]
    locationlimit = SelectField(label='Limit', coerce=int, choices=choices)

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    choices = [('Mr', 'Mr'), ('Mrs', 'Mrs'), ('Ms', 'Ms'), ('Dr', 'Dr')]
    title = SelectField(label='Title', choices=choices)
    firstname = StringField(label='First Name', validators=[DataRequired(), Length(min=3, max=20)])
    lastname = StringField(label='Family Name', validators=[DataRequired(), Length(min=3, max=20)])
    position = StringField(label='Position')
    email = StringField(label='Email', validators=[DataRequired(), Email()])
    address = StringField(label='Address')
    phone = StringField(label='Phone')
    dob = DateField(label='Date of Birth', format='%Y-%m-%d', validators=[DataRequired()])
    
    
class EditWorkshopTypeForm(FlaskForm):
    workshoptype = StringField(label='Workshop Type', validators=[DataRequired(),Length(min=3,max=100)])
    workshopdesc = TextAreaField(label='Workshop Common Description', render_kw={"rows": 10})

class EditLessonTypeForm(FlaskForm):
    lessontype = StringField(label='Lesson Type', validators=[DataRequired(),Length(min=3,max=100)])
    lessondesc = TextAreaField(label='Lesson Common Description', render_kw={"rows": 10})

#create flaskform for add lesson form
class AddTutorLessonForm(FlaskForm):
    title = SelectField(label='Select Title')
    location = SelectField(label='Select Location')
    lessondate = DateField(label='Lesson Date')
    lessonstarttime = TimeField(label='Start Time')
    lessondesc = TextAreaField(label='Lesson Description', render_kw={"rows": 6})

#create flaskform for edit lesson form
class EditTutorLessonForm(FlaskForm):
    title = SelectField(label='Select Title', coerce=int)
    location = SelectField(label='Select Location', coerce=int)
    lessondate = DateField(label='Lesson Date')
    lessonstarttime = TimeField(label='Start Time')
    lessondesc = TextAreaField(label='Lesson Description', render_kw={"rows": 6})

#create flaskform for all user change password form
class ChangePasswordForm(FlaskForm):
    current_password = PasswordField(label='Current Password',validators=[DataRequired(),Length(min=8,max=12)])
    password = PasswordField(label='Password',validators=[DataRequired(),Length(min=8,max=12)])
    confirm_password = PasswordField(label='Confirm Password',validators=[DataRequired(),EqualTo('password')])
    submit = SubmitField(label='Submit')

class editPricesForm(FlaskForm):
    annualsubfee = DecimalField(label='Annual ($):', validators=[InputRequired(), NumberRange(min=0.01)])
    monthlysubfee = DecimalField(label='Monthly ($):', validators=[InputRequired(), NumberRange(min=0.01)])
    monthlysubdiscount = DecimalField(label='Monthly Discount (%):', validators=[InputRequired(), NumberRange(min=0.01)])
    annualsubdiscount = DecimalField(label='Annual Discount (%):', validators=[InputRequired(), NumberRange(min=0.01)])
    lessonfee = DecimalField(label='Lesson ($):', validators=[InputRequired(), NumberRange(min=0.01)])
    submit = SubmitField(label='Submit')



#create flaskform for adding a lesson (manager)
class AddaLessonForm(FlaskForm):
    title = SelectField(label='Select Title', validators=[DataRequired()])
    location = SelectField(label='Select Location', validators=[DataRequired()])
    tutor = SelectField(label='Select Tutor', validators=[DataRequired()])
    lessondate = DateField(label='Lesson Date', validators=[DataRequired()])
    lessonstarttime = TimeField(label='Start Time', validators=[DataRequired()])
    lessondesc = TextAreaField(label='Lesson Description', render_kw={"rows": 6}, validators=[DataRequired()])

#create flaskform for editing a lesson (manager)
class EditaLessonForm(FlaskForm):
    title = SelectField(label='Select Title', coerce=int, validators=[DataRequired()])
    location = SelectField(label='Select Location', coerce=int, validators=[DataRequired()])
    tutor = SelectField(label='Select Tutor',  coerce=int, validators=[DataRequired()])
    lessondate = DateField(label='Lesson Date', validators=[DataRequired()])
    lessonstarttime = TimeField(label='Start Time', validators=[DataRequired()])
    lessondesc = TextAreaField(label='Lesson Description', render_kw={"rows": 6}, validators=[DataRequired()])

class NewsForm(FlaskForm):
    title = StringField('News Title', validators=[DataRequired()])
    text = TextAreaField('Description', validators=[DataRequired()])
    images = MultipleFileField('', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!'),
        validators.Length(max=1, message='You can upload up to 1 image only.')])
    newsdate = DateField(label='Date Added')

class EditNewsForm(FlaskForm):
    title = StringField('News Title', validators=[DataRequired()])
    text = TextAreaField('Description', validators=[DataRequired()])
    images = MultipleFileField('', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!'),
        validators.Length(max=1, message='You can upload up to 1 image only.')])
    newsdate = DateField(label='Date Added')

class MemberSubscriptionForm(FlaskForm):
    status = StringField('Subscription Status')
    subscription = StringField('Subscription Plan')
    expirydate = DateField(label='Expiry Date')

