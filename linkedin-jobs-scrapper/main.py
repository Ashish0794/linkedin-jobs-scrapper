import re
from configparser import ConfigParser, ExtendedInterpolation
from functools import partial
from time import sleep

from tenacity import retry, stop_after_attempt, wait_fixed

from LinkedInJobScrapper import JobScrapper

config = ConfigParser(interpolation=ExtendedInterpolation(), allow_no_value=True)
config.SECTCRE = re.compile(r"\[ *(?P<header>[^]]+?) *\]")
config.read(
    "E:\\Dev-Data-Projects\\PythonProjects\\linkedin-jobs-scraper\\linkedin-jobs-scrapper\\config.ini"
)

retry_attempt = 2

retry_on_error = partial(
    retry,
    stop=stop_after_attempt(retry_attempt),
    wait=wait_fixed(0.4),
)()


class LinkedInJobExtraction:
    def __init__(self) -> None:
        """Parameter initialization"""

        self.site_url = config["DEFAULT"]["SITE_URL"]
        self.site_entry_page_url = config["DEFAULT"]["SITE_ENTRY_PAGE_URL"]
        self.username = config["DEFAULT"]["USERNAME"]
        self.password = config["DEFAULT"]["PASSWORD"]
        self.job_keyword = config["JOBS_PARAMS"]["JOB_KEYWORD"]
        self.job_location = config["JOBS_PARAMS"]["JOB_LOCATION"]
        self.premium_org = config["JOBS_PARAMS"]["PREMIUM_ORGS"]
        self.additional_filter = config["JOBS_PARAMS"]["ADDITIONAL_FILTER"]
        self.target_file_name = config["TARGET_PARAMS"]["TARGET_FILE_NAME"]
        self.target_location = config["TARGET_PARAMS"]["TARGET_LOCATION"]

    @retry_on_error
    def extract(self) -> None:
        try:
            bot = JobScrapper(
                site_url=self.site_url,
                site_entry_page_url=self.site_entry_page_url,
                username=self.username,
                password=self.password,
                job_keyword=self.job_keyword,
                job_location=self.job_location,
                premium_org=self.premium_org,
                additional_filter=self.additional_filter,
                target_file_name=self.target_file_name,
                target_location=self.target_location,
            )
            bot.user_login()
            sleep(3)
            bot.job_search()
            sleep(5)
            bot.job_filter()
            sleep(5)
            bot.job_extract()
            sleep(1)
            bot.user_logout()

        except:
            print(f"Job extraction process failed. Retrying.")
            raise Exception

        print("Linkedin job extraction completed!!")


if __name__ == "__main__":
    job = LinkedInJobExtraction()
    job.extract()
