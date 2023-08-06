class ChapmanError(Exception): pass
class ConfigError(ChapmanError): pass
class UnknownTaskError(ChapmanError): pass
class InvalidPayloadError(ChapmanError): pass
