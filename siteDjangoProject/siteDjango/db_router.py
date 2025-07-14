class DatabaseRouter:
    """
    Router para direcionamento de banco de dados
    - Blog models: banco 'blog'
    - Outros models: banco 'default'
    """
    
    def db_for_read(self, model, **hints):
        """Escolher banco para leitura"""
        if model._meta.app_label == 'mapa_eleitoral' and model.__name__.lower() in ['blogarticle', 'blogarticleview']:
            return 'blog'
        return 'default'

    def db_for_write(self, model, **hints):
        """Escolher banco para escrita"""
        if model._meta.app_label == 'mapa_eleitoral' and model.__name__.lower() in ['blogarticle', 'blogarticleview']:
            return 'blog'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """Permitir relações entre objetos do mesmo banco"""
        db_set = {'default', 'blog'}
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Controlar quais migrations vão para qual banco"""
        if app_label == 'mapa_eleitoral' and model_name and model_name.lower() in ['blogarticle', 'blogarticleview']:
            return db == 'blog'
        elif app_label == 'mapa_eleitoral':
            return db == 'default'
        return db == 'default'