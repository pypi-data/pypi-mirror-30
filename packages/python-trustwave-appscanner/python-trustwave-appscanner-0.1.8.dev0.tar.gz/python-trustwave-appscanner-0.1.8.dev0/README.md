Python Trustwave Appscanner
===========================

Python Trustwave Appscanner transforms Appscanner REST API results into Plain Python Objects for easier processing.

Installation
------------

`pip install python-trustwave-appscanner`

Usage
-----

The library exposes some functions that can return Python objects representing the XML response, strings or booleans.

Boolean functions are: `application_exists`, `assessment_exists`

String functions are: `get_application_id_by_name`, `get_assessment_status`, `get_current_assessment_run_id`

`get_assessment_run_status` returns an `AssessmentRun` object,

``