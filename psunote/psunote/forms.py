from flask_wtf import FlaskForm
from wtforms import Field, widgets, StringField, TextAreaField

import models


class TagListField(Field):
    widget = widgets.TextInput()

    def __init__(self, label="", validators=None, remove_duplicates=True, **kwargs):
        super().__init__(label, validators, **kwargs)
        self.remove_duplicates = remove_duplicates
        self.data = []

    def process_formdata(self, valuelist):
        if valuelist and valuelist[0]:
            data = [x.strip() for x in valuelist[0].split(",") if x.strip()]
            
            if self.remove_duplicates:
                self.data = []
                for d in data:
                    if d not in self.data:
                        self.data.append(d)
            else:
                self.data = data
        else:
            self.data = []

    def _value(self):
        if self.data:
            return ", ".join(self.data)
        return ""


class BaseNoteForm(FlaskForm):
    title = StringField("Title")
    description = TextAreaField("Description")


class NoteForm(BaseNoteForm):
    tags = TagListField("Tag")
