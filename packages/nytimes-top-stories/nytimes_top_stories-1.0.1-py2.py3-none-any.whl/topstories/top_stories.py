import json
import requests

class APIKeyError(Exception):
    pass

class InvalidFormatType(Exception):
    pass

class InvalidSectionType(Exception):
    pass

class InvalidAuthentication(Exception):
    pass

class TopStoriesAPI():

    def __init__(self, key=None):
        """
        Initializes a TopStoriesAPI object.

        params:
            key: (string) API key from https://developer.nytimes.com

        """
        self.key = key
        self.url = "https://api.nytimes.com/svc/topstories/v2/{}.{}?api-key={}"

        if self.key is None:
            raise APIKeyError("""An API key is required. Please register for an API key at
                                https://developer.nytimes.com/signup.""")

    def get_sections_list(self):
        """
        Returns a list of valid story sections.
        return:
            list

        """
        return ["home", "opinion","world","national","politics","upshot","nyregion","business",
                "technology","science","health","sports","arts","books","theater","sundayreview",
                "fashion","tmagazine","food","travel","magazine","realestate","automobiles",
                "obituaries","insider"]


    def get_stories(self, section, format_type="json", return_json_string=False):
        """

        Gets a list of current top articles and associated images in the
        specified section and in the specified format.

        params:
            section: (string) the section the articles appears in
            format: (string) json or jsonp, default is json
            return_json_string: (boolean) if True, return value will be JSON string instead of a python list,
                                default is False
        return:
            If format type is json, a list of articles (articles are python dicts) is returned.
            If format type is jsonp, API returns a callback function (string) in the format
                "{section}TopStoriesCallback({data})". JSON data is an object not an array and data is
                not parsed/decoded.
        """

        self._validate_args(section, format_type)

        request = self.url.format(section.lower(), format_type, self.key)

        response = self._get_response(request)

        #data is wrapped in a callback function, so return text
        if format_type == "jsonp":
            return response.text

        results = response.json()["results"]

        return json.dumps(results) if return_json_string else results

    def write_to_json_file(self, path_to_file, stories_list):
        """
        Writes a python list of stories into a json file.

        params:
            path_to_file: (string) path to the json file the data will be written in
            stories_list: (list) list returned from the self.get_stories method
        """
        try:
            with open(path_to_file, "w+") as file:
                json.dump(stories_list, file)
        except EnvironmentError as e:
            raise e

    def _get_response(self, request):
        """
        Helper function.
        Gets a Response object from the API call.
        Raises an HTTPError if status code is not between 200-400 or
        an InvalidAuthentication exception if the API key is not valid.

        """
        try:
            response = requests.get(request)

            if "Invalid authentication credentials" in response.text:
                raise InvalidAuthentication("Invalid authentication credentials. Please try a different API key.")

            response.raise_for_status()

            return response

        except requests.HTTPError as e:
                raise e

    def _validate_args(self, section, format_type):
        """
        Helper function.
        Validates the arguments given in the self.get_stories method.
        If any arguments were invalid, an exception is raised.
        """
        self._validate_section(section)

        self._validate_format_type(format_type)

    def _validate_section(self, section):
        """
        Helper function.
        Validates {section} argument given in the self.get_stories method.
        Raises an InvalidSectionType exception if {section} was invalid.
        """
        sections = self.get_sections_list()

        if section not in sections:
            raise InvalidSectionType("%s is not a valid story section. Valid sections include: %s."
                                      % (section, sections))

    def _validate_format_type(self, format_type):
        """
        Helper function.
        Validates {format_type} argument given in the self.get_stories method.
        Raises an InvalidFormatType exception if {format_type} was invalid.
        """
        if format_type != "json" and format_type != "jsonp":
            raise InvalidFormatType("%s is not a valid format type. Valid format types include json and jsonp."
                                     % (format_type,))
