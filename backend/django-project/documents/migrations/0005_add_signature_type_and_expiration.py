# Generated manually for CertiSign signature types feature

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0004_add_organization_name_and_signer_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentsignature',
            name='signature_type',
            field=models.CharField(
                choices=[('permanent', 'Pérenne'), ('ephemeral', 'Éphémère')],
                default='permanent',
                help_text='Type de signature : pérenne (valide indéfiniment) ou éphémère (avec date d\'expiration)',
                max_length=20,
                verbose_name='Type de signature'
            ),
        ),
        migrations.AddField(
            model_name='documentsignature',
            name='expiration_date',
            field=models.DateTimeField(
                blank=True,
                help_text='Date d\'expiration pour les signatures éphémères. Laissez vide pour les signatures pérennes.',
                null=True,
                verbose_name='Date d\'expiration'
            ),
        ),
    ] 