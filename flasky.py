import os
from flask_migrate import Migrate
from app import create_app, db
from app.models import User, Role, RegisterCheckOutFile

app = create_app(os.getenv('FLASK_CONFIG') or 'default')            # 应用工厂函数
# migrate = Migrate(app, db)              # 使用Flask-Migrate实现数据库迁移


# @app.shell_context_processor          # 创建并注册一个shell 上下文处理器
# def make_shell_context():
#     return dict(db=db, User=User, Role=Role, RegisterCheckOutFile=RegisterCheckOutFile)


# @app.cli.command()
# def test():
#     """Run the unit tests."""
#     import unittest
#     tests = unittest.TestLoader().discover('tests')
#     unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == '__main__':
    app.run()
