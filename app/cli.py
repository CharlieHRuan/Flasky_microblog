import click
import os


def register(app):
    @app.cli.group()
    def translate():
        """
        翻译及本地化命令
        """
        pass

    @translate.command()
    def update():
        """
        更新所有语言
        """
        if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
            raise RuntimeError('extract command failed')
        if os.system('pybabel update -i messages.pot -d app/translations'):
            raise RuntimeError('update command failed')
        # 更新完成后，删除这个文件，因为再次需要的时候可以很容易生成
        os.remove('messages.pot')

    @translate.command()
    def compile():
        """
        编译所有语言
        """
        if os.system('pybabel compile -d app/translations'):
            raise RuntimeError('compile command failed')

    @translate.command()
    @click.argument('lang')
    def init(lang):
        """
        初始化语言
        """
        if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
            raise RuntimeError('extract command failed')
        if os.system(
                'pybabel init -i messages.pot -d app/translations -l' + lang):
            raise RuntimeError('init command failed')
        os.remove('messages.pot')
