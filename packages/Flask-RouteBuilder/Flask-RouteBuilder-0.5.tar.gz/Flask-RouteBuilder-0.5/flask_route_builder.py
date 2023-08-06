import pkgutil

from flask import current_app


def format_route(blueprint):
    return ('blueprints.{0}.main'.format(blueprint), blueprint)


class RouterBuilder(object):
    def __init__(self, app=None):
        
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        with app.app_context():
            app.config.setdefault('ROUTER_BUILDER_URL_PREFIX', None)
            
            # List all blueprints in the application blueprints package and return a list of tuples with (url, module_name)
            blue_prints = [format_route(module_name) for _, module_name, _ in pkgutil.iter_modules(['blueprints'])]
            
            # Register blueprints 
            for module_path, module_name in blue_prints:
                blue_print = __import__(module_path, globals(), locals(), [module_name], 0)
                
                if current_app.config['ROUTER_BUILDER_URL_PREFIX'] is not None:
                    current_app.register_blueprint(getattr(blue_print, module_name),
                                                    url_prefix='/{0}/{1}'.format(
                                                        current_app.config['ROUTER_BUILDER_URL_PREFIX'], module_name))
                else:
                    current_app.register_blueprint(getattr(blue_print, module_name),
                                                   url_prefix='/{0}'.format(module_name))
