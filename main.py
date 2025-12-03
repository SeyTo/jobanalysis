import json
import os

from pandas import DataFrame

from models.job import Job
from services.create_report import create_report
from utils.os_stuff import notify_and_open_report

location = [("remote", 1)]
# should be a file
# import keywords_w_weights =
# import section_titles =
# import markers

# check title extract keywords -> weight measure -> if weight <0 then reject return
# by spacy extract keywords + surrounding verbs+auxiliaries to check if certain tech is being used or not.
#

# return yes/no, weights, original link, paragraphs, keywords(w original text), technologies, responsibilities, company link


def load_jobs_to_classes(jobs_data: DataFrame):
    jobs: list[Job] = []
    for data in jobs_data.itertuples(index=False):
        job = Job(
            job_title=data.job_title,
            job_description=data.job_description,
            job_description_url=data.job_description_url,
            company_name=data.company_name,
            company_desc=data.company_desc,
            company_num_employees=data.company_num_employees,
            company_url=data.company_url,
            markers=data.markers,
            is_remote=data.is_remote,
            location=data.location,
        )

        jobs.append(job)

    return jobs


def run():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "b.json")
    with open(file_path) as f:
        jobs_data = DataFrame.from_dict(json.load(f), orient="columns")
    jobs_data.head()

    jobs = load_jobs_to_classes(jobs_data=jobs_data)

    report_name = create_report(jobs=jobs)

    # delete_scraping_results_from_backup_folder()
    # notify_and_open_report(report_name)


if __name__ == "__main__":
    run()
