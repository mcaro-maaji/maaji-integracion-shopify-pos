"""TODO: DOCS"""

from setuptools import setup, find_packages

setup(
    name="maaji_integracion_shopify_pos",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "webdriver-manager==4.0.2",
        "selenium==4.26.1",
        "requests==2.32.3",
        "dataclasses-json==0.6.7",
        "click==8.1.7"
    ],
    entry_points={
        'console_scripts': [
            'maaji-integracion-shopify-pos = maaji_integracion_shopify_pos:main',
        ]
    },
)
