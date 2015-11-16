#!/usr/bin/env python

from flask.ext.script import Manager
import myownmocker

manager = Manager(myownmocker.app)


@manager.command
def initdb():
    """Create the database tables"""
    print 'Using database %s' % myownmocker.db.engine.url
    myownmocker.db.create_all()
    print 'Created tables'


if __name__ == '__main__':
    manager.run()
