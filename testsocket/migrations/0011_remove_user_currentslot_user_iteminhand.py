# Generated by Django 5.1.7 on 2025-03-25 00:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('testsocket', '0010_rename_armorslot_user_armor_rename_hoeslot_user_hoe_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='currentSlot',
        ),
        migrations.AddField(
            model_name='user',
            name='itemInHand',
            field=models.CharField(default='weapon', max_length=10),
        ),
    ]
