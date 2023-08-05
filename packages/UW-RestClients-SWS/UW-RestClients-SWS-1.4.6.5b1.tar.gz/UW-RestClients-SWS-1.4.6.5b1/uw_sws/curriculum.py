"""
Interfacing with the Student Web Service, Curriculum Search Resource.
"""
import logging
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode
from uw_sws.models import Curriculum
from uw_sws import get_resource


logger = logging.getLogger(__name__)
curriculum_search_url_prefix = "/student/v5/curriculum.json"


def get_curricula_by_department(department, future_terms=0):
    """
    Returns a list of restclients.Curriculum models, for the passed
    Department model.
    """
    if not isinstance(future_terms, int):
        raise ValueError(future_terms)

    if future_terms < 0 or future_terms > 2:
        raise ValueError(future_terms)

    url = "%s?%s" % (
        curriculum_search_url_prefix,
        urlencode([("department_abbreviation", department.label,),
                   ("future_terms", future_terms,)]))
    return _json_to_curricula(get_resource(url))


def get_curricula_by_term(term):
    """
    Returns a list of restclients.Curriculum models, for the passed
    Term model.
    """
    url = "%s?%s" % (
        curriculum_search_url_prefix,
        urlencode([
                   ("quarter", term.quarter.lower(),),
                   ("year", term.year,),
                   ]))
    return _json_to_curricula(get_resource(url))


def _json_to_curricula(data):
    curricula = []
    for curr_data in data.get("Curricula", []):
        curriculum = Curriculum()
        curriculum.label = curr_data["CurriculumAbbreviation"]
        curriculum.name = curr_data["CurriculumName"]
        curriculum.full_name = curr_data["CurriculumFullName"]
        curriculum.clean_fields()
        curricula.append(curriculum)

    return curricula
