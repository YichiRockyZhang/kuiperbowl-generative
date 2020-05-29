# Generated by Django 2.2.7 on 2020-05-29 00:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0008_remove_player_muted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='tag',
            field=models.CharField(choices=[('join', 'join'), ('leave', 'leave'), ('buzz_init', 'buzz_init'), ('buzz_correct', 'buzz_correct'), ('buzz_wrong', 'buzz_wrong'), ('buzz_forfeit', 'buzz_forfeit'), ('set_category', 'set_category'), ('set_difficulty', 'set_difficulty'), ('reset_score', 'reset_score'), ('chat', 'chat')], max_length=20),
        ),
    ]
