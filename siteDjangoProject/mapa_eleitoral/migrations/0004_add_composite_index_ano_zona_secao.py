"""
Migration para adicionar índice composto (ano_eleicao, zona_secao)
que otimiza a query de get_zonas_secoes_ajax (de ~34s para <1s).
"""
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mapa_eleitoral', '0003_blogarticle_blogarticleview'),
    ]

    operations = [
        migrations.RunSQL(
            sql="CREATE INDEX idx_ano_zona_secao ON eleicoes_rio (ANO_ELEICAO, ZONA_SECAO);",
            reverse_sql="DROP INDEX idx_ano_zona_secao ON eleicoes_rio;",
        ),
    ]
