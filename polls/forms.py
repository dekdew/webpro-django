from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core import validators
from django.core.exceptions import ValidationError

from polls.models import Poll, Question, Choice, Comment


def validate_even(value):
  if value % 2 != 0:
    raise ValidationError('%(value)s ไม่ใช่เลขคู่', params={'value':value})
  return value

class PollForm(forms.Form):
  title = forms.CharField(label="ชื่อโพล", max_length=100, required=True)
  email = forms.CharField(validators=[validators.validate_email])
  no_question = forms.IntegerField(label="จำนวนคำถาม", min_value=0, max_value=10, required=True, validators=[validate_even])
  start_date = forms.DateField(required=False)
  end_date = forms.DateField(required=False)

  def clean_title(self):
    data = self.cleaned_data['title']

    if "ไอที" not in data:
      raise forms.ValidationError("คุณลืมชื่อคณะ")

    return data

  def clean(self):
    cleaned_data = super().clean()
    start = cleaned_data.get('start_date')
    end = cleaned_data.get('end_date')

    if start and not end:
      # raise forms.ValidationError("เลือกวันที่สิ้นสุด")
      self.add_error('end_date', 'เลือกวันที่สิ้นสุด')

    elif end and not start:
      # raise forms.ValidationError("เลือกวันที่เริ่มต้น")
      self.add_error('start_date', 'เลือกวันที่เริ่มต้น')


class QuestionForm(forms.Form):
  question_id = forms.IntegerField(widget=forms.HiddenInput, required=False)
  text = forms.CharField(widget=forms.Textarea, required=False)
  type = forms.ChoiceField(choices=Question.TYPES, initial='01', required=False)


class ChoiceModelForm(forms.ModelForm):
  class Meta:
    model = Choice
    fields = '__all__'


class PollModelForm(forms.ModelForm):
  class Meta:
    model = Poll
    exclude = ['del_flag']

  def clean_title(self):
    data = self.cleaned_data['title']

    if "ไอที" not in data:
      raise forms.ValidationError("คุณลืมชื่อคณะ")

    return data

  def clean(self):
    cleaned_data = super().clean()
    start = cleaned_data.get('start_date')
    end = cleaned_data.get('end_date')

    if start and not end:
      # raise forms.ValidationError("เลือกวันที่สิ้นสุด")
      self.add_error('end_date', 'เลือกวันที่สิ้นสุด')

    elif end and not start:
      # raise forms.ValidationError("เลือกวันที่เริ่มต้น")
      self.add_error('start_date', 'เลือกวันที่เริ่มต้น')


def phone_validate(value):
  if not value.isdigit():
    raise forms.ValidationError("หมายเลขโทรศัพท์ต้องเป็นตัวเลขเท่านั้น")
  if len(value) != 10:
    raise forms.ValidationError("หมายเลขโทรศัพท์ต้องมี 10 หลัก")
  return value

class CommentForm(forms.Form):
  title = forms.CharField(max_length=100)
  body = forms.CharField(max_length=500, widget=forms.Textarea)
  email = forms.EmailField(required=False)
  tel = forms.CharField(required=False, max_length=10, validators=[phone_validate])

  def clean(self):
    cleaned_data = super().clean()
    email = cleaned_data.get('email')
    tel = cleaned_data.get('tel')

    if not email and not tel:
      raise forms.ValidationError("ต้องกรอก email หรือ Mobile Number")


class CommentModelForm(forms.ModelForm):
  class Meta:
    model = Comment
    exclude = ['poll']

  def clean(self):
    cleaned_data = super().clean()
    email = cleaned_data.get('email')
    tel = cleaned_data.get('tel')

    if not email and not tel:
      raise forms.ValidationError("ต้องกรอก email หรือ Mobile Number")


class ChangePasswordForm(forms.Form):
  def __init__(self, user, *args, **kwargs):
    self.user = user
    super(ChangePasswordForm, self).__init__(*args, **kwargs)

  old_password = forms.CharField(required=True, widget=forms.PasswordInput)
  new_password = forms.CharField(min_length=8, required=True, widget=forms.PasswordInput)
  confirm_password = forms.CharField(min_length=8, required=True, widget=forms.PasswordInput)

  def clean(self):
    cleaned_data = super().clean()
    old_password = cleaned_data.get('old_password')
    new = cleaned_data.get('new_password')
    confirm = cleaned_data.get('confirm_password')

    print(self.user.password)
    if self.user.check_password('{}'.format(old_password)) == False:
      raise forms.ValidationError('"รหัสผ่านเก่า" ไม่ถูกต้อง')

    if new != confirm:
      raise forms.ValidationError('"รหัสผ่านใหม่" กับ "ยืนยันรหัสผ่าน" ต้องเหมือนกัน')


class ProfileForm(UserCreationForm):
  email = forms.EmailField()
  line_id = forms.CharField(required=False)
  facebook = forms.CharField(required=False)
  MALE = 'M'
  FEMALE = 'F'
  OTHER = 'X'
  GENDER = (
    (MALE, 'ชาย'),
    (FEMALE, 'หญิง'),
    (OTHER, 'อื่น ๆ')
  )
  gender = forms.ChoiceField(choices=GENDER)
  birthdate = forms.DateField(required=False)

