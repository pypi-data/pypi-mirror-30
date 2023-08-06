from ScopusWp.extend import ExtensionInstallationController

from ScopusWp.wordpress.config import PATH, NAME
from ScopusWp.wordpress.reference import BASE

import os


if __name__ == '__main__':
    install = ExtensionInstallationController(NAME)
    install.create_mysql_database('__wordpress', BASE)

    template = install.load_template(os.path.join(PATH, 'templates', 'config.ini'))
    content = template.render(
        url='',
        password='',
        username=''
    )

    install.create_file('config.ini', content)
