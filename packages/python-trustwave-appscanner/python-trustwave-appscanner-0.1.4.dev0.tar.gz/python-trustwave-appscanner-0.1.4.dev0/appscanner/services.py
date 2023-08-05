import datetime
import os

from lxml import etree
from tapioca_trustwave import Trustwave

from appscanner.exceptions import AppscannerClientError
from appscanner.model import AssessmentRuns, AssessmentRunResults, AssessmentRun
from .validators import validate_uuid4, validate_application_name

yesterday = (datetime.datetime.utcnow() - datetime.timedelta(days=1)).strftime(
    '%Y-%m-%dT%H:%MhZ')

server = os.environ.get('TRUSTWAVE_APPSCANNER_SERVER')
client = os.environ.get('TRUSTWAVE_APPSCANNER_CLIENT')
customer = os.environ.get('TRUSTWAVE_APPSCANNER_CUSTOMER')

api = Trustwave(server=server, client=client, customer=customer)
STATUS_OK = 0


def trim_encoding_declaration(xml):
    lines = list(map(str.strip, xml.splitlines()))
    return ''.join(lines[1:]) if 'encoding' in lines[0] else ''.join(lines)


def application_exists(application_id):
    validate_uuid4(application_id)

    request = api.get_application_id_by_name(
        application_id=application_id).get()
    application_data = request().data

    application_exists = application_data.get('application-exists')
    return application_exists


def get_application_id_by_name(application_name):
    validate_application_name(application_name)

    request = api.get_application_id_by_name(
        application_name=application_name).get()
    application_data = request().data

    application_id = application_data.get('application-id')
    return application_id


def assessment_exists(application_id, assessment_id):
    validate_uuid4(application_id)
    validate_uuid4(assessment_id)

    request = api.check_if_assessment_exists(application_id=application_id,
                                             assessment_id=assessment_id).get()
    assessment_data = request().data

    assessment_exists = assessment_data.get('assessment-exists')
    return assessment_exists


def get_assessment_id_by_name(application_id, assessment_name):
    validate_uuid4(application_id)

    request = api.get_assessment_id_by_name(application_id=application_id,
                                            assessment_name=assessment_name).get()
    assessment_data = request().data

    assessment_id = assessment_data.get('assessment-id')
    return assessment_id


def get_assessment_status(application_id, assessment_id):
    validate_uuid4(application_id)
    validate_uuid4(assessment_id)

    request = api.get_assessment_status(application_id=application_id,
                                        assessment_id=assessment_id).get()
    assessment_data = request().data

    status = assessment_data.get('assessment-status')
    return status


def get_current_assessment_run_id(application_id, assessment_id,
                                  get_exclude_runs=False,
                                  start_date_time=yesterday):
    validate_uuid4(application_id)
    validate_uuid4(assessment_id)

    params = {
        'getExcludedRuns': get_exclude_runs,
        'startDateTime': start_date_time
    }

    request = api.get_assessment_runs(
        application_id=application_id,
        assessment_id=assessment_id
    ).get(params=params)
    assessment_run_results_data = request().data

    status_code = assessment_run_results_data.get('status-code')
    if status_code == STATUS_OK:
        assessment_run_results = trim_encoding_declaration(
            assessment_run_results_data.get('assessment-runs'))
        run_info = AssessmentRuns.from_etree(etree.XML(assessment_run_results))

        for assessment_run in run_info.data:
            if assessment_run.Status == 'running':
                oldest_assessment_run_id = assessment_run.AssessmentRunId
                return oldest_assessment_run_id

    return None


def get_assessment_run_status(application_id, assessment_run_id):
    validate_uuid4(application_id)
    validate_uuid4(assessment_run_id)

    request = api.get_assessment_run_status(application_id=application_id,
                                            assessment_run_id=assessment_run_id).get()
    assessment_data = request().data

    status = AssessmentRun.from_etree(etree.XML(
        trim_encoding_declaration(assessment_data.get('assessment-status'))))

    return status


def get_assessment_run_results(application_id, assessment_run_id):
    validate_uuid4(application_id)
    validate_uuid4(assessment_run_id)

    request = api.get_assessment_runs(application_id=application_id,
                                      assessment_run_id=assessment_run_id).get()
    assessment_run_results_data = request().data

    assessment_run_results = AssessmentRunResults.from_etree(etree.XML(
        trim_encoding_declaration(
            assessment_run_results_data.get('assessment-run-results'))))
    return assessment_run_results


def queue_assessment(application_id, assessment_id, test_only=False):
    validate_uuid4(application_id)
    validate_uuid4(assessment_id)

    params = {
        'test-only': test_only
    }

    try:
        request = api.queue_assessment(application_id=application_id,
                                       assessment_id=assessment_id)
        request = request.put(data=params)
        assessment_data = request().data
    except Exception as e:
        raise AppscannerClientError

    status = assessment_data.get('status-code')
    return status
