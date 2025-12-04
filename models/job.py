import logging
from dataclasses import dataclass
from types import NoneType

from services.job_analysis import score_job_description


@dataclass
class Job:
    job_title: str
    job_description_url: str
    company_name: str
    markers: str | None
    company_desc: str | None
    company_num_employees: str | None
    company_url: str | None
    company_location: str
    job_description_text: str
    job_description_html: str
    is_remote: str
    rating: int
    posting_site: str | None

    def __init__(
        self,
        job_title: str,
        job_description_url: str,
        company_name: str,
        markers: str | None,
        company_desc: str | None,
        company_num_employees: str | None,
        company_url: str | None,
        job_description_text: str,
        job_description_html: str,
        is_remote: str,
        company_location: str,
        posting_site: str | None,
    ):
        # todo - handle nans that we have instead of None
        self.job_title = " ".join(job_title.split())
        self.job_description_url = " ".join(job_description_url.split())
        self.company_name = " ".join(company_name.split())
        self.markers = " ".join(markers.split())
        self.company_desc = " ".join(company_desc.split())
        self.company_num_employees = " ".join(company_num_employees.split())
        self.company_url = " ".join(company_url.split())
        self.job_description_text = " ".join(job_description_text.split())
        self.job_description_html = " ".join(job_description_html.split())
        self.is_remote = " ".join(is_remote.split())
        self.company_location = " ".join(company_location.split())
        self.posting_site = " ".join(posting_site.split())

        try:
            _rating = 0
            # todo - move this to main.py instead of doing this while loading the dataclass (in case of specific error)
            if type(self.job_description_text) != "":
                _rating = score_job_description(self.job_description_text).score
        except Exception as e:
            _rating = 0
            logging.exception(e)
            pass

        self.rating = _rating
