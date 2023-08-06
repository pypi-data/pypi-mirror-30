# cmsplugin-survey

This django CMS plugin lets editors add simple surveys into the pages.

![Front End](/screenshots/example.png?raw=true "Front End")

## installation

1. Install *cmsplugin_survey* package.
  ```bash
  pip install cmsplugin-survey
  ```

2. Add *cmsplugin_survey* package into your INSTALLED_APPS.
  ```python
  INSTALLED_APPS = [
    ...
    'cmsplugin_survey',
    ...
  ]
  ```

3. Add *cmsplugin_suvery.urls* into your project's url configuration.
  ```python
  from django.conf.urls import url, include

  urlpatterns = [
    ...
    url(r'^survey/', include('cmsplugin_survey.urls')),
    ...
  ]
  ```

4. Create database layout.
  ```bash
  ./manage.py migrate
  ```

## Usage

Create and manage the surveys in django admin site.
![Admin Form](/screenshots/adminform.png?raw=true "Admin Form")

## Configuration

You may set ```CMSPLUGIN_SURVEY_TEMPLATES``` setting to let editor choose from different templates.
