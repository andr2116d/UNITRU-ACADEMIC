class SuvError(Exception):
    pass


class CaptchaError(SuvError):
    pass


class AuthenticationError(SuvError):
    pass


class NavigationError(SuvError):
    pass


class ExtractionError(SuvError):
    pass


class SuvTimeoutError(SuvError):
    pass


class SuvUnavailableError(SuvError):
    pass


class GradesTableNotFoundError(ExtractionError):
    pass


class AcademicInfoNotFoundError(ExtractionError):
    pass


class InvalidCourseRowError(ExtractionError):
    pass


class GradeMappingError(ExtractionError):
    pass
