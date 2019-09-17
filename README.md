# 2019-web-services-project-skeleton

This is a tutorial how to setup and use the framework.

## Settings

First thing first, you need to check all packages in the `requirements.txt` file. 
They should be automatically detect and install by Python Interpreter.

There are some attributes in `settings.py` file that you need to pay attention.

`SECRET_KEY`: It is empty in the beginning. It should be unique and you have to generate one 
to be able to run the project. You can generate a key by using an online generator like this 
[Djecrety](https://djecrety.ir/); or by the below code in Python console:
```
>>> import random
>>> ''.join(random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50))
```

`INSTALLED_APPS`: A list of strings of used packages and apps in this project. It is split into 
`PREREQ_APPS` and `PROJECT_APPS` for clarity reasons. The former consists of Django packages and 
the latter contains project user-defined apps. One can freely add more packages or apps 
if needed in their appropriate locations.

`TEMPLATES`, `STATIC_URL` and `STATICFILES_DIRS`: These are kept as default as in Django 
convention. So, the folder that contains HTML files and the one that contains JS and CSS files 
name `templates` and `static` respectively.

`AUTH_PASSWORD_VALIDATORS`: A list of strings for types of password validators. 
In the beginning, it is empty for the sake of testing.

## Structure

The project comes with two apps, auction and user. All required URLs are provided in `urls.py` 
files of the project and apps. The `views.py` files have empty functions that are ready 
to be implemented. 

Students are open to make new apps if they want but they need to make sure to follow the 
convention on the templates and static folders.

## Tests

In the inner Yaas directory, there is `testsTDD.py` containing all the tests. Students are not 
allowed to make any change to this file. If they want to create their own tests, they should 
create a file named `test*.py` and write tests in there because Python 3 automatically discover 
tests in any file with that name when running. There are several ways to run the tests from 
PyCharm or commands:

- PyCharm:
    * Choose the test file and click the Run button on the Toolbar.
    * Press `Ctrl-Alt-R` (for Window).
    * Right click on the file and then Run tests.
    * Click a run button at the beginning of a test case or a test to run them specifically.
- `manage.py` commands:
```
# Run all the tests
$ ./manage.py test

# Run all the tests found within the 'auction' package
$ ./manage.py test auction

# Run all the tests in the yaas.testsTDD module
$ ./manage.py test yaas.testsTDD

# Run just one test case
$ ./manage.py test yaas.testsTDD.SignUpTests

# Run just one test method
$ ./manage.py test yaas.testsTDD.SignUpTests.test_sign_up_with_valid_data
```

## Automated grading

During the implementation, students can run the tests frequently to check what features they 
have done and how many points they currently have. Each use case from the requirements is a 
test case, they will give a message after they are run, and only when all tests of a test case 
pass, students can receive points granted by it. The result message should be something similar 
to this: `UC1 passed, 1 point, Current points: 1/30`.
