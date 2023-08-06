from setuptools import setup, find_packages

version = "0.1.3"

setup(
    name="true_case",
    version=version,
    description="Get case statistics for words.",
    author="Brian Lester",
    author_email="blester125@gmail.com",
    license="MIT",
    python_requires='>=3.6',
    packages=find_packages(),
    package_data={
        'true_case': [
            'true_case/data/model.p',
        ],
    },
    install_requires=[
        'tqdm',
    ],
    include_package_data=True,
    keywords=["NLP"]
)
