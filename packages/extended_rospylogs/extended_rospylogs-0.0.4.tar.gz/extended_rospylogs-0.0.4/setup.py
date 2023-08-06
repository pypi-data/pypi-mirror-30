from setuptools import setup, find_packages

with open("README.md", "r") as readme:
    setup(
        name = "extended_rospylogs",
        version = "0.0.4",
        author = "Carlos Alvarez",
        author_email = "candres.alve@gmail.com",
        description = "Extension of logs for rospy based con roscpp.",
        long_description = readme.read(),
        license = "MIT",
        keywords = [],
        url = "https://github.com/charlielito/extended_rospylogs",
        packages = find_packages(),
        package_data={},
        include_package_data = True,
        install_requires = []
    )
