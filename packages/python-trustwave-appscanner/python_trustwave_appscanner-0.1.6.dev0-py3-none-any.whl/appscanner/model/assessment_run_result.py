from collections import UserList

from lxml import etree

from .helpers import process_datetime_element, process_int_element, \
    process_text_element, process_nested_text_element


class SmartAttackInfo:
    def __init__(self, PolicyId, PolicyVersion, CenzicId, Severity,
                 VulnerabilityIds, SmartAttackName, Description,
                 TechnicalDescription, HowItWorks, Impact, Remediation):
        self.PolicyId = PolicyId
        self.PolicyVersion = PolicyVersion
        self.CenzicId = CenzicId
        self.Severity = Severity
        self.VulnerabilityIds = VulnerabilityIds
        self.SmartAttackName = SmartAttackName
        self.Description = Description
        self.TechnicalDescription = TechnicalDescription
        self.HowItWorks = HowItWorks
        self.Impact = Impact
        self.Remediation = Remediation

    @staticmethod
    def from_etree(elem):
        assert isinstance(elem, etree._Element)
        assert elem.tag == 'SmartAttackInfo'

        PolicyId = elem.attrib.get('PolicyId')
        PolicyVersion = elem.attrib.get('PolicyVersion')
        CenzicId = elem.attrib.get('CenzicId')
        Severity = elem.attrib.get('Severity')
        VulnerabilityIds = elem.attrib.get('VulnerabilityIds')
        SmartAttackName = process_text_element(elem.find('SmartAttackName'))
        Description = process_text_element(elem.find('Description'))
        TechnicalDescription = process_text_element(
            elem.find('TechnicalDescription'))
        HowItWorks = process_text_element(elem.find('HowItWorks'))
        Impact = process_text_element(elem.find('Impact'))
        Remediation = process_text_element(elem.find('Remediation'))

        return SmartAttackInfo(PolicyId, PolicyVersion, CenzicId, Severity,
                               VulnerabilityIds, SmartAttackName, Description,
                               TechnicalDescription, HowItWorks, Impact,
                               Remediation)


class ReportItem:
    def __init__(self, Id, ReportItemType, ReportItemCreateDate, Severity,
                 HarmScore, CVSSBaseScore, ComputedHarmScore, Count,
                 Message, GlobalizedMessage, Url, TraversalName,
                 Filtered, HttpRequest, HttpResponse, StructuredData):
        self.Id = Id
        self.ReportItemType = ReportItemType
        self.ReportItemCreateDate = ReportItemCreateDate
        self.Severity = Severity
        self.HarmScore = HarmScore
        self.CVSSBaseScore = CVSSBaseScore
        self.ComputedHarmScore = ComputedHarmScore
        self.Count = Count
        self.Message = Message
        self.GlobalizedMessage = GlobalizedMessage
        self.Url = Url
        self.TraversalName = TraversalName
        self.Filtered = Filtered
        self.HttpRequest = HttpRequest
        self.HttpResponse = HttpResponse
        self.StructuredData = StructuredData

    @staticmethod
    def from_etree(elem):
        assert isinstance(elem, etree._Element)

        Id = elem.attrib['Id']
        ReportItemType = process_text_element(elem.find('ReportItemType'))
        ReportItemCreateDate = process_datetime_element(
            elem.find('ReportItemCreateDate'))
        Severity = process_text_element(elem.find('Severity'))
        HarmScore = process_int_element(elem.find('HarmScore'))
        CVSSBaseScore = process_text_element(elem.find('CVSSBaseScore'))
        ComputedHarmScore = process_int_element(elem.find('ComputedHarmScore'))
        Count = process_int_element(elem.find('Count'))
        Message = process_text_element(elem.find('Message'))
        GlobalizedMessage = process_text_element(
            elem.find('GlobalizedMessage'))
        Url = process_text_element(elem.find('Url'))
        TraversalName = process_text_element(elem.find('TraversalName'))
        Filtered = process_int_element(elem.find('Filtered'))
        HttpRequest = process_text_element(elem.find('HttpRequest'))
        HttpResponse = process_text_element(elem.find('HttpResponse'))
        StructuredData = process_text_element(elem.find('StructuredData'))

        return ReportItem(Id, ReportItemType, ReportItemCreateDate, Severity,
                          HarmScore, CVSSBaseScore, ComputedHarmScore, Count,
                          Message, GlobalizedMessage, Url, TraversalName,
                          Filtered, HttpRequest, HttpResponse, StructuredData)


class Category:
    def __init__(self, Name):
        self.Name = Name

    @staticmethod
    def from_etree(xml_etree):
        assert isinstance(xml_etree, etree._Element)

        Name = xml_etree.find('Name').text

        return Category(Name)


class Categories(UserList):
    @staticmethod
    def from_etree(xml_etree):
        assert isinstance(xml_etree, etree._Element)
        assert xml_etree.tag == 'Categories'

        categories = [Category(category) for category in
                      xml_etree.findall('Category')]

        return Categories(categories)


class PagesVisited(UserList):
    @staticmethod
    def from_etree(xml_etree):
        assert isinstance(xml_etree, etree._Element)
        assert xml_etree.tag == 'PagesVisited'

        Urls = [url.text for url in xml_etree.findall('Url')]

        return PagesVisited(Urls)


class ReportItems(UserList):
    @staticmethod
    def from_etree(xml_etree):
        assert isinstance(xml_etree, etree._Element)
        assert xml_etree.tag == 'ReportItems'

        report_items = [ReportItem.from_etree(item) for item in
                        xml_etree.findall('ReportItem')]

        return ReportItems(report_items)


class SmartAttacksData:
    def __init__(self, smart_attack_info, report_items, categories):
        self.SmartAttackInfo = smart_attack_info
        self.ReportItems = report_items
        self.Categories = categories

    @staticmethod
    def from_etree(xml_etree):
        assert isinstance(xml_etree, etree._Element)
        assert xml_etree.tag == 'SmartAttacksData'

        smart_attack_info = SmartAttackInfo.from_etree(
            xml_etree.find('SmartAttackInfo'))
        report_items = ReportItems.from_etree(
            xml_etree.find('ReportItems'))
        categories = Categories(xml_etree.find('Categories'))

        return SmartAttacksData(smart_attack_info, report_items,
                                categories)


class SmartAttacks(UserList):
    @staticmethod
    def from_etree(elem):
        assert isinstance(elem, etree._Element)
        assert elem.tag == 'SmartAttacks'

        smart_attacks = [SmartAttacksData.from_etree(item) for item in
                         elem.findall('SmartAttacksData')]

        return SmartAttacks(smart_attacks)


class AssessmentRunInfo:
    def __init__(self, HarmScore, RiskFactor, Status, AttackCount,
                 MaxPagesVisited, StartTime, EndTime):
        self.HarmScore = HarmScore
        self.RiskFactor = RiskFactor
        self.Status = Status
        self.AttackCount = AttackCount
        self.MaxPagesVisited = MaxPagesVisited
        self.StartTime = StartTime
        self.EndTime = EndTime

    @staticmethod
    def from_etree(elem):
        assert isinstance(elem, etree._Element)

        HarmScore = process_int_element(elem.find('HarmScore'))
        RiskFactor = process_int_element(elem.find('RiskFactor'))
        Status = process_text_element(elem.find('Status'))
        AttackCount = process_int_element(elem.find('AttackCount'))
        MaxPagesVisited = process_int_element(
            elem.find('MaxPagesVisited'))
        StartTime = process_datetime_element(elem.find('StartTime'))
        EndTime = process_datetime_element(elem.find('EndTime'))

        return AssessmentRunInfo(HarmScore, RiskFactor, Status, AttackCount,
                                 MaxPagesVisited, StartTime, EndTime)


class AssessmentRunData:
    def __init__(self, request_id, assessment_run_id, assessment_name,
                 application_name, application_id, application_url,
                 assessment_run_info, smart_attacks, pages_visited,
                 status_analysis):
        self.RequestId = request_id
        self.AssessmentRunId = assessment_run_id
        self.AssessmentName = assessment_name
        self.ApplicationName = application_name
        self.ApplicationId = application_id
        self.ApplicationUrl = application_url
        self.AssessmentRunInfo = assessment_run_info
        self.SmartAttacks = smart_attacks
        self.PagesVisited = pages_visited
        self.StatusAnalysis = status_analysis

    @staticmethod
    def from_etree(elem):
        assert isinstance(elem, etree._Element)

        request_id = elem.attrib['RequestId']
        assessment_run_id = elem.attrib['AssessmentRunId']
        assessment_name = elem.attrib['AssessmentName']
        application_name = elem.attrib['ApplicationName']
        application_id = elem.attrib['ApplicationId']
        application_url = elem.attrib['ApplicationUrl']

        assessment_run_info = AssessmentRunInfo.from_etree(
            elem.find('AssessmentRunInfo'))
        smart_attacks = SmartAttacks.from_etree(elem.find('SmartAttacks'))
        pages_visited = PagesVisited.from_etree(elem.find('PagesVisited'))

        status_analysis = process_nested_text_element(elem, 'ASMSummaryData.asmInfo.statusAnalysis')

        return AssessmentRunData(request_id, assessment_run_id,
                                 assessment_name,
                                 application_name, application_id,
                                 application_url, assessment_run_info,
                                 smart_attacks, pages_visited, status_analysis)


class Assessments(UserList):
    @staticmethod
    def from_etree(elem):
        assert isinstance(elem, etree._Element)
        assert elem.tag == 'Assessments'

        assessments = [AssessmentRunData.from_etree(assessment) for assessment
                       in elem.findall('AssessmentRunData')]

        return Assessments(assessments)
