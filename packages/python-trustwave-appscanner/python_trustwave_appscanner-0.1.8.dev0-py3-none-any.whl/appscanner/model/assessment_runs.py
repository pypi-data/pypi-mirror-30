from collections import UserList

from lxml import etree

from .helpers import process_text_element, process_int_element, \
    process_datetime_element


class AssessmentRun:
    def __init__(self, AssessmentRunId, StartTime, EstimatedStartTime, EndTime,
                 Status, PagesVisited, TotalHARM, ASMStatus, Progress,
                 LowVulnerabilityScore, MedVulnerabilityScore,
                 HighVulnerabilityScore, ApproximateHarmScore, PagesSeen,
                 TimeElapsed, TimeRemaining, AttackCount, RequestCount,
                 ShortText, LongText, VulCount, WarnCount, InfoCount,
                 LastProgress, LastProcessing, ChunkNumber, TotalChunks,
                 LowWarningScore, MedWarningScore, HighWarningScore):
        self.AssessmentRunId = AssessmentRunId
        self.StartTime = StartTime
        self.EstimatedStartTime = EstimatedStartTime
        self.EndTime = EndTime
        self.Status = Status
        self.PagesVisited = PagesVisited
        self.TotalHARM = TotalHARM
        self.ASMStatus = ASMStatus
        self.Progress = Progress
        self.LowVulnerabilityScore = LowVulnerabilityScore
        self.MedVulnerabilityScore = MedVulnerabilityScore
        self.HighVulnerabilityScore = HighVulnerabilityScore
        self.ApproximateHarmScore = ApproximateHarmScore
        self.PagesSeen = PagesSeen
        self.TimeElapsed = TimeElapsed
        self.TimeRemaining = TimeRemaining
        self.AttackCount = AttackCount
        self.RequestCount = RequestCount
        self.ShortText = ShortText
        self.LongText = LongText
        self.VulCount = VulCount
        self.WarnCount = WarnCount
        self.InfoCount = InfoCount
        self.LastProgress = LastProgress
        self.LastProcessing = LastProcessing
        self.ChunkNumber = ChunkNumber
        self.TotalChunks = TotalChunks
        self.LowWarningScore = LowWarningScore
        self.MedWarningScore = MedWarningScore
        self.HighWarningScore = HighWarningScore

    @staticmethod
    def from_etree(elem):
        assert isinstance(elem, etree._Element)

        assessment_run_id = process_text_element(elem.find('AssessmentRunId'))
        start_time = process_datetime_element(elem.find('StartTime'))
        estimated_start_time = process_datetime_element(
            elem.find('EstimatedStartTime'))
        end_time = process_datetime_element(elem.find('EndTime'))
        status = process_text_element(elem.find('Status'))
        pages_visited = process_int_element(elem.find('PagesVisited'))
        total_HARM = process_int_element(elem.find('TotalHARM'))
        ASM_status = process_text_element(elem.find('ASMStatus'))
        progress = process_text_element(elem.find('Progress'))
        low_vulnerability_score = process_int_element(
            elem.find('LowVulnerabilityScore'))
        med_vulnerability_score = process_int_element(
            elem.find('MedVulnerabilityScore'))
        high_vulnerability_score = process_int_element(
            elem.find('HighVulnerabilityScore'))
        approximate_harm_score = process_int_element(
            elem.find('ApproximateHarmScore'))
        pages_seen = process_int_element(elem.find('PagesSeen'))
        time_elapsed = process_text_element(elem.find('TimeElapsed'))
        time_remaining = process_text_element(elem.find('TimeRemaining'))
        attack_count = process_int_element(elem.find('AttackCount'))
        request_count = process_int_element(elem.find('RequestCount'))
        short_text = process_text_element(elem.find('ShortText'))
        long_text = process_text_element(elem.find('LongText'))
        vul_count = process_int_element(elem.find('VulCount'))
        warn_count = process_int_element(elem.find('WarnCount'))
        info_count = process_int_element(elem.find('InfoCount'))
        last_progress = process_datetime_element(elem.find('LastProgress'))
        last_processing = process_text_element(elem.find('LastProcessing'))
        chunk_number = process_int_element(elem.find('ChunkNumber'))
        total_chunks = process_int_element(elem.find('TotalChunks'))
        low_warning_score = process_int_element(elem.find('LowWarningScore'))
        med_warning_score = process_int_element(elem.find('MedWarningScore'))
        high_warning_score = process_int_element(elem.find('HighWarningScore'))

        return AssessmentRun(assessment_run_id, start_time,
                             estimated_start_time, end_time, status,
                             pages_visited, total_HARM, ASM_status, progress,
                             low_vulnerability_score, med_vulnerability_score,
                             high_vulnerability_score, approximate_harm_score,
                             pages_seen, time_elapsed, time_remaining,
                             attack_count, request_count, short_text,
                             long_text,
                             vul_count, warn_count, info_count, last_progress,
                             last_processing, chunk_number, total_chunks,
                             low_warning_score, med_warning_score,
                             high_warning_score)


class AssessmentRuns(UserList):
    @staticmethod
    def from_etree(elem):
        assert isinstance(elem, etree._Element)
        assert elem.tag == 'AssessmentRuns'

        assessments = [AssessmentRun.from_etree(assessment) for assessment in
                       elem.findall('AssessmentRun')]

        return AssessmentRuns(assessments)
