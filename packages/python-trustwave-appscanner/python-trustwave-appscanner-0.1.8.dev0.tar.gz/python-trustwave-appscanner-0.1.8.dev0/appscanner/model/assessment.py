from collections import UserList

from lxml import etree

from .helpers import process_text_element


class Assessment:
    def __init__(self, assessment_id, assessment_name, is_api_safe, url,
                 application_id):
        self.AssessmentId = assessment_id
        self.AssessmentName = assessment_name
        self.IsApiSafe = is_api_safe
        self.Url = url
        self.ApplicationId = application_id

    @staticmethod
    def from_etree(elem):
        assert isinstance(elem, etree._Element)

        assessment_id = process_text_element(elem.find('AssessmentId'))
        assessment_name = process_text_element(elem.find('AssessmentName'))
        is_api_safe = bool(elem.find('IsApiSafe').text)
        url = process_text_element(elem.find('Url'))
        application_id = process_text_element(elem.find('ApplicationId'))

        return Assessment(assessment_id, assessment_name, is_api_safe, url,
                          application_id)


class Assessments(UserList):
    @staticmethod
    def from_etree(xml_etree):
        assert isinstance(xml_etree, etree._Element)
        assert xml_etree.tag == 'Assessments'

        assessments = [Assessment.from_etree(assessment) for assessment in xml_etree.findall('Assessment')]

        return Assessments(assessments)