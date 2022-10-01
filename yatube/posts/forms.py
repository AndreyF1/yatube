from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Текст поста',
            'group': 'Группа'
        }
        help_texts = {
            'text': 'Напишите ваш пост здесь',
            'group': 'Выбери группу для поста'
        }

    def clean_text(self):
        data = self.cleaned_data['text']
        if len(data) < 3:
            raise forms.ValidationError('Ваш пост слишком короткий')
        return data


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)

    def clean_text(self):
        data = self.cleaned_data['text']
        if len(data) < 3:
            raise forms.ValidationError('Ваш комментарий слишком короткий')
        return data
