# Generated by Django 4.2 on 2023-04-24 23:45

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Mailing',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('content_text', models.TextField(verbose_name='Текст рассылки')),
                ('content_image', models.ImageField(blank=True, null=True, upload_to='', verbose_name='Медиа рассылки (фото)')),
                ('content_video', models.FileField(blank=True, null=True, upload_to='', verbose_name='Медиа рассылки (видео)')),
            ],
            options={
                'verbose_name': 'Рассылка',
                'verbose_name_plural': 'Рассылки',
            },
        ),
        migrations.CreateModel(
            name='MailingButtons',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('button_text', models.CharField(max_length=200, verbose_name='Тескт кнопки')),
                ('mailing_link', models.URLField(verbose_name='Ссылка для кнопки')),
                ('mail', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mail_link', to='mailing.mailing')),
            ],
            options={
                'verbose_name': 'Ссылка',
                'verbose_name_plural': 'Ссылки',
            },
        ),
    ]
