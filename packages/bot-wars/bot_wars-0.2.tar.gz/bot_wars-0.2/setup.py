from setuptools import setup


setup(name="bot_wars",
      version="0.2",
      packages=["bot_wars"],
      license="BSD2CLAUSE",
      scripts=['scripts/bot_wars'],
      url="https://github.com/kanazux/bot-wars",
      author_email="contato@kanazuchi.com",
      description="A simple telegram bot to get mob info.",
      install_requires=['bs4',
                        'requests',
                        'requests-html',
                        'python-telegram-bot'],
      zip_safe=False)
