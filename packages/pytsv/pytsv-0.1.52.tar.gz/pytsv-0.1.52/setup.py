import setuptools

"""
The documentation can be found at:
http://setuptools.readthedocs.io/en/latest/setuptools.html
"""
setuptools.setup(
    # the first three fields are a must according to the documentation
    name='pytsv',
    version='0.1.52',
    packages=[
        'pytsv',
        'pytsv.scripts',
    ],
    # from here all is optional
    description='pytsv is a module to help with all things TSV',
    long_description='pytsv is a module to help with all things TSV',
    author='Mark Veltzer',
    author_email='mark.veltzer@gmail.com',
    maintainer='Mark Veltzer',
    maintainer_email='mark.veltzer@gmail.com',
    keywords=[
        'python',
        'tsv',
        'format',
        'csv',
    ],
    url='https://veltzer.github.io/pytsv',
    download_url='https://github.com/veltzer/pytsv',
    license='MIT',
    platforms=[
        'python2',
    ],
    install_requires=[
        'click',
        'tqdm',
        'pyanyzip',
        'numpy',
        'futures',
        'pandas',
        'pylogconf',
        'attrs',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ],
    data_files=[
    ],
    entry_points={'console_scripts': [
        'pytsv_aggregate=pytsv.scripts.aggregate:main',
        'pytsv_check=pytsv.scripts.check:main',
        'pytsv_check_columns_unique=pytsv.scripts.check_columns_unique:main',
        'pytsv_clean_by_field_num=pytsv.scripts.clean_by_field_num:main',
        'pytsv_csv_to_tsv=pytsv.scripts.csv_to_tsv:main',
        'pytsv_cut=pytsv.scripts.cut:main',
        'pytsv_drop_duplicates_by_columns=pytsv.scripts.drop_duplicates_by_columns:main',
        'pytsv_fix_columns=pytsv.scripts.fix_columns:main',
        'pytsv_histogram_by_column=pytsv.scripts.histogram_by_column:main',
        'pytsv_join=pytsv.scripts.join:main',
        'pytsv_lc=pytsv.scripts.lc:main',
        'pytsv_majority=pytsv.scripts.majority:main',
        'pytsv_multiply=pytsv.scripts.multiply:main',
        'pytsv_read=pytsv.scripts.read:main',
        'pytsv_remove_quotes=pytsv.scripts.remove_quotes:main',
        'pytsv_sample_by_column=pytsv.scripts.sample_by_column:main',
        'pytsv_sample_by_column_old=pytsv.scripts.sample_by_column_old:main',
        'pytsv_sample_by_two_columns=pytsv.scripts.sample_by_two_columns:main',
        'pytsv_split_by_columns=pytsv.scripts.split_by_columns:main',
        'pytsv_sum=pytsv.scripts.sum:main',
        'pytsv_tree=pytsv.scripts.tree:main',
        'pytsv_tsv_to_csv=pytsv.scripts.tsv_to_csv:main',
    ]},
    python_requires='>=2.7',
)
