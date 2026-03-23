class ResumeAnalyzerError(Exception):
    pass


class PDFExtractionError(ResumeAnalyzerError):
    pass


class AnalysisServiceError(ResumeAnalyzerError):
    pass


class AnalysisNotFoundError(ResumeAnalyzerError):
    pass
