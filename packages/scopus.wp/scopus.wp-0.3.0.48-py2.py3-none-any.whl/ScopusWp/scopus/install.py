from ScopusWp.extend import ExtensionInstallationController

import ScopusWp.scopus.persistency as ps
from ScopusWp.register import OriginType
from ScopusWp.scopus.config import PATH, NAME

import os


if __name__ == '__main__':
    install = ExtensionInstallationController(NAME)
    install.create_mysql_database('__scopus', ps.BASE)

    install.explorer.session.add(OriginType(typeID=1, name='scopus'))

    template = install.load_template(os.path.join(PATH, 'templates', 'config.ini'))
    content = template.render(
        shorthand='SHORTHAND',
        ids=[],
        first_name='',
        last_name='',
        keywords=[],
        whitelist=[],
        blacklist=[]
    )

    install.create_file('config.ini', content)
