from setuptools import setup, find_packages  
  
setup(  
      name='gdby',   #名称  
      version='0.15',  #版本  
      description="a tool for generating special db format yaml", #描述  
      keywords='',  
      author='sea',  #作者  
      author_email='sealevelnn@163.com', #作者邮箱  
      packages=["generate_yaml"],  
      install_requires=[      #需求的第三方模块  
        'requests',  
      ],  
      entry_points={
        'console_scripts': [
            'gdby=generate_yaml.generate_yaml:generate_yaml'
        ]
    }
)  