class Errors():
    """
    Manages errors for toy funnel
    """

    def __init__(self):
        """
        Initialize class
        """
        self._errors = {}

        self._errors[1000] = "Unknown Error"

        self._errors[2000] = "Unknown error loading data"
        self._errors[2010] = "Too many group matches, check format of self.funnel_params in Config"

        self._errors[3000] = "Unknown error analyzing funnel"
        self._errors[3010] = "Number of customers from previous stage = 0"


    def get_error(self, code, traceback=None, details=None):
        """
        Return error text and additional information for a given code
        traceback = traceback output
        details = additional details about the error
        """

        if code in self._errors:
            error_text = self._errors[code]
        else:
            error_text = "Unknown Error"


        error = {"code": code, "text": error_text}
        if traceback is not None:
            error['traceback'] = traceback
        if details is not None:
            error['details'] = details


        return error


