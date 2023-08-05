# coding: utf-8

from flask_security import Security
from flask_ldap3_login import LDAP3LoginManager
from flask_migrate import Migrate
from flask_cache import Cache
from flask_mail import Mail
from flask_celery import Celery
from flask_htmlmin import HTMLMIN
from flask_assets import Environment, Bundle
from flask_debugtoolbar import DebugToolbarExtension
from flask_wtf.csrf import CSRFProtect
from flask_marshmallow import Marshmallow
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy, Model
from sqlalchemy_repr import RepresentableBase

"""Extensions used by Modis Lock application

"""

__all__ = ['security', 'ldap_manager', 'marshmallow', 'csrf_protect', 'html_min', 'cache', 'mail', 'celery',
           'assets', 'migrate', 'debug_toolbar', 'rest_api', 'db', 'asset_bundles']


class ReprBaseClass(RepresentableBase, Model):
    def __init__(self):
        pass


security = Security()
ldap_manager = LDAP3LoginManager()
migrate = Migrate()
marshmallow = Marshmallow()
csrf_protect = CSRFProtect()
html_min = HTMLMIN()
cache = Cache()
mail = Mail()
celery = Celery()
assets = Environment()
debug_toolbar = DebugToolbarExtension()
rest_api = Api()
db = SQLAlchemy(model_class=ReprBaseClass)


# These represent the CSS and JS libraries used by each controller. They are compiled at installation for faster access
asset_bundles = {
    'welcome_css': Bundle('css/libs/jquery.steps.css',
                          'css/libs/jquery-ui-1.10.3.custom.css',
                          'css/libs/bootstrap-datetimepicker.css',
                          'css/libs/awesome-bootstrap-checkbox.css',
                          '../pages/welcome/welcome.css',
                          filters='cssmin',
                          output='css/welcome_css.css'),
    'welcome_js': Bundle('js/libs/jquery.steps.js',
                         'js/libs/pwstrength.js',
                         'js/libs/transition.js',
                         'js/libs/collapse.js',
                         'js/libs/bootstrap-datetimepicker.js',
                         '../pages/welcome/welcome.js',
                         filters='jsmin',
                         output='js/welcome_js.js'),
    'layout_css': Bundle('css/libs/bootstrap.css',
                         'css/libs/font-awesome.css',
                         'css/animate.css',
                         'css/style.css',
                         'css/libs/toastr.css',
                         filters='cssmin',
                         output='css/layout_css.css'),
    'layout_js': Bundle('js/libs/jquery-3.2.1.js',
                        'js/libs/bootstrap.js',
                        'js/libs/metisMenu.js',
                        'js/libs/jquery.slimscroll.js',
                        'js/libs/moment.js',
                        'js/inspinia.js',
                        'js/libs/toastr.js',
                        'js/layout.js',
                        Bundle('js/libs/pace.min.js'),
                        filters='jsmin',
                        output='js/layout_js.js'),
    'tables_css': Bundle('plugins/DataTables-1.10.15/media/css/dataTables.bootstrap.css',
                         'plugins/DataTables-1.10.15/extensions/Responsive/css/responsive.bootstrap.css',
                         'plugins/DataTables-1.10.15/extensions/Buttons/css/buttons.bootstrap.css',
                         'plugins/DataTables-1.10.15/extensions/Select/css/select.bootstrap.css',
                         'plugins/DataTables-1.10.15/extensions/Scroller/css/scroller.bootstrap.css',
                         'plugins/jquery-datatables-checkboxes-1.2.10/css/dataTables.checkboxes.css',
                         'plugins/Editor-1.6.2/css/editor.bootstrap.css',
                         'css/libs/awesome-bootstrap-checkbox.css',
                         filters='cssmin',
                         output='css/tables_css.css'),
    'tables_js': Bundle('plugins/DataTables-1.10.15/media/js/jquery.dataTables.js',
                        'plugins/DataTables-1.10.15/media/js/dataTables.bootstrap.js',
                        'plugins/DataTables-1.10.15/extensions/Buttons/js/dataTables.buttons.js',
                        'plugins/DataTables-1.10.15/extensions/Buttons/js/buttons.bootstrap.js',
                        'plugins/DataTables-1.10.15/extensions/Responsive/js/dataTables.responsive.js',
                        'plugins/DataTables-1.10.15/extensions/Responsive/js/responsive.bootstrap.js',
                        'plugins/DataTables-1.10.15/extensions/Select/js/dataTables.select.js',
                        'plugins/DataTables-1.10.15/extensions/Scroller/js/dataTables.scroller.js',
                        'plugins/jquery-datatables-checkboxes-1.2.10/js/dataTables.checkboxes.js',
                        'plugins/Editor-1.6.2/js/dataTables.editor.js',
                        'plugins/Editor-1.6.2/js/editor.bootstrap.js',
                        filters='jsmin',
                        output='js/tables_js.js'),
    'index_js': Bundle('plugins/chartJs/Chart.js',
                       '../pages/index/index.js',
                       filters='jsmin',
                       output='js/index_js.js'),
    'users_css': Bundle('css/libs/bootstrap-toggle.css',
                        'css/libs/jquery.steps.css',
                        'css/libs/jquery-ui-1.10.3.custom.css',
                        'css/libs/funkyradio.css',
                        '../pages/users/users.css',
                        filters='cssmin',
                        output='css/users_css.css'),
    'users_js': Bundle('js/libs/jquery.steps.js',
                       'js/libs/u2f-api.js',
                       'js/libs/bootstrap-toggle.js',
                       'js/libs/bootstrap-confirmation.js',
                       Bundle('js/libs/jquery-ui-1.10.3.custom.min.js'),
                       '../pages/users/common.js',
                       '../pages/users/user_edit.js',
                       '../pages/users/ldap_user.js',
                       filters='jsmin',
                       output='js/users_js.js'),
    'logs_css': Bundle(Bundle('css/libs/vis-timeline-graph2d.min.css'),
                       'css/libs/bootstrap-datetimepicker.css',
                       'css/libs/daterangepicker.css',
                       '../pages/logs/logs.css',
                       filters='cssmin',
                       output='css/logs_css.css'),
    'logs_js': Bundle('js/libs/vis.js',
                      'js/libs/bootstrap-datetimepicker.js',
                      Bundle('js/libs/vis-timeline-graph2d.min.js'),
                      'js/libs/daterangepicker.js',
                      '../pages/logs/logs.js',
                      filters='jsmin',
                      output='js/logs_js.js'),
    'select_css': Bundle('css/libs/select2.css',
                         'css/libs/select2-bootstrap.css',
                         filters='cssmin',
                         output='css/select_css.css'),
    'select_js': Bundle('js/libs/select2.full.js',
                        filters='jsmin',
                        output='js/select_js.js'),
    'settings_css': Bundle('css/libs/bootstrap-toggle.css',
                           'css/libs/jquery.bootstrap-touchspin.css',
                           'css/libs/ion.rangeSlider.css',
                           'css/libs/ion.rangeSlider.skinFlat.css',
                           'plugins/clockpicker-gh-pages/src/clockpicker.css',
                           'css/libs/awesome-bootstrap-checkbox.css',
                           'css/libs/bootstrap-datetimepicker.css',
                           Bundle('plugins/Ladda-1.0.6/css/ladda-themeless.min.css'),
                           '../pages/settings/settings.css',
                           filters='cssmin',
                           output='css/settings_css.css'),
    'settings_js': Bundle('js/libs/bootstrap-confirmation.js',
                          'js/libs/bootstrap-toggle.js',
                          'js/libs/jquery.bootstrap-touchspin.js',
                          'js/libs/ion.rangeSlider.js',
                          'plugins/clockpicker-gh-pages/src/clockpicker.js',
                          'js/libs/icheck.js',
                          'js/libs/bootstrap-filestyle.js',
                          'js/libs/bootstrap-confirmation.js',
                          'js/libs/bootstrap-datetimepicker.js',
                          'plugins/Ladda-1.0.6/js/spin.js',
                          'plugins/Ladda-1.0.6/js/ladda.js',
                          '../pages/settings/settings_network.js',
                          '../pages/settings/settings_api.js',
                          '../pages/settings/settings_ldap.js',
                          '../pages/settings/settings_backup.js',
                          '../pages/settings/settings_system.js',
                          '../pages/settings/settings_reader.js',
                          '../pages/settings/settings_rules.js',
                          '../pages/settings/settings_alerts.js',
                          '../pages/settings/settings.js',
                          filters='jsmin',
                          output='js/settings_js.js')
}
