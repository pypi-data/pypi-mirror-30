import json

from lxml import etree

from .services import get_assessment_run_results, trim_encoding_declaration
from appscanner.model import AssessmentRunResults, AssessmentRuns, Assessments


def assessment_run_results_factory(api_results):
    elem = etree.XML(
        trim_encoding_declaration(
            json.loads(api_results)['assessment-run-results']
        )
    )

    return AssessmentRunResults.from_etree(elem)


def assessment_runs_factory(api_results):
    elem = etree.XML(
        trim_encoding_declaration(
            json.loads(api_results)['assessment-runs']
        )
    )

    return AssessmentRuns.from_etree(elem)


def assessments_factory(api_results):
    elem = etree.XML(
        trim_encoding_declaration(
            json.loads(api_results)['assessments']
        )
    )

    return AssessmentRuns.from_etree(elem)
