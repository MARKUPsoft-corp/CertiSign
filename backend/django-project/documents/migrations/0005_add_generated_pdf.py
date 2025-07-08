# Generated manually on 2024-01-XX XX:XX

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0004_add_organization_name_and_signer_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentqrposition',
            name='generated_pdf',
            field=models.FileField(blank=True, null=True, upload_to='documents/generated/', verbose_name='PDF généré avec QR'),
        ),
    ] 