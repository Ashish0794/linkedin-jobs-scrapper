import re
from time import sleep

import pandas as pd
import undetected_chromedriver.v2 as uc
from bs4 import BeautifulSoup as bs
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class JobScrapper:
    def __init__(
        self,
        site_url,
        site_entry_page_url,
        username,
        password,
        job_keyword,
        job_location,
        premium_org,
        additional_filter,
        target_file_name,
        target_location,
    ) -> None:
        """Parameter initialization"""

        self.site_url = site_url
        self.site_entry_page_url = site_entry_page_url
        self.username = username
        self.password = password
        self.job_keyword = job_keyword
        self.job_location = job_location
        self.premium_org = premium_org
        self.additional_filter = additional_filter
        self.target_file_name = target_file_name
        self.target_location = target_location

        options = uc.ChromeOptions()
        options.headless = False
        options.add_argument("--headless")
        self.driver = uc.Chrome(options=options)
        self.driver.implicitly_wait(10)

    def user_login(self) -> None:
        """This function logs into personal profile"""

        self.driver.get(self.site_url)

        # Enter username and password

        login_username = self.driver.find_element(by=By.NAME, value="session_key")
        login_username.clear()
        login_username.send_keys(self.username)

        login_password = self.driver.find_element(by=By.NAME, value="session_password")
        login_password.clear()
        login_password.send_keys(self.password)

        try:
            # Hit enter for login

            login_password.send_keys(Keys.RETURN)

            # Validate for successful login attempt

            post_success_url = self.site_entry_page_url

            if self.driver.current_url == post_success_url:
                print("Login Success")
        except:
            print("Login Fail")

    def job_search(self) -> None:
        """This function goes to the 'Jobs' section and search for the jobs matching keywords and location"""

        # go to Jobs

        job_link = self.driver.find_element(by=By.LINK_TEXT, value="Jobs")
        job_link.click()
        # sleep(5)

        # search based on keywords and location and hit enter

        search_keywords = self.driver.find_element(
            by=By.XPATH,
            value="//input[starts-with(@id, 'jobs-search-box-keyword')]",
        )
        search_keywords.clear()
        search_keywords.send_keys(self.job_keyword)
        # sleep(5)

        search_location = self.driver.find_element(
            by=By.XPATH,
            value="//input[starts-with(@id, 'jobs-search-box-location')]",
        )
        search_location.clear()
        search_location.send_keys(self.job_location)
        sleep(2)

        search_location.send_keys(Keys.RETURN)

    def job_filter(self) -> None:
        """This function filters all the job results based on 'Job Type' & 'Date Posted' values"""

        # select all filters, choose Past 24 hours and Full-time button  and apply the filter

        parent_filter_button = self.driver.find_element(
            by=By.XPATH,
            value="//button[contains(@aria-label,'Show all filters')]",
        )
        parent_filter_button.click()
        sleep(1)

        date_Filter_button = self.driver.find_element(
            by=By.CSS_SELECTOR,
            value="input[value='r86400']",
        )
        self.driver.execute_script("arguments[0].click();", date_Filter_button)
        sleep(1)

        job_type_Filter_button = self.driver.find_element(
            by=By.CSS_SELECTOR,
            value="input[value='F']",
        )

        self.driver.execute_script("arguments[0].click();", job_type_Filter_button)

        Filter_button = self.driver.find_element(
            by=By.XPATH,
            value="//button[contains(@aria-label,'Apply current filters')]",
        )
        self.driver.execute_script("arguments[0].click();", Filter_button)
        sleep(5)

        total_results = self.driver.find_element(
            by=By.CLASS_NAME,
            value="display-flex.t-12.t-black--light.t-normal",
        )
        self.total_results_count = re.search(r"\d+", total_results.text)[0]

        print(f"Total jobs results after applying filter - {self.total_results_count}")

    def job_extract(self) -> None:
        """This function extracts jobs from all the page results to a csv file"""

        current_page_number = 1

        additional_filter_list = self.additional_filter.split(",")
        additional_filter_list = [check.strip() for check in additional_filter_list]

        premium_org_list = self.premium_org.split(",")
        premium_org_list = [name.strip() for name in premium_org_list]

        df = pd.DataFrame(
            columns=[
                "Job_ID",
                "Job_Title",
                "Organization",
                "Organization_Type",
                "Job_Location",
                "LinkedIn_Job_Link",
                "Job_Industy",
                # "Skill_Match",
                "Job_Description",
            ]
        )

        while True:
            jobs_section = self.driver.find_elements(
                by=By.CLASS_NAME,
                value="jobs-search-results__list-item.occludable-update.p0.relative.ember-view",
            )

            for section in jobs_section:

                hover = ActionChains(self.driver).move_to_element(section)
                hover.perform()

                job_container = section.find_elements(
                    by=By.CLASS_NAME, value="job-card-container"
                )

                job_id = section.find_element(
                    by=By.CSS_SELECTOR, value="div.job-card-container"
                ).get_attribute("data-job-id")

                for job in job_container:

                    job_title = job.find_element(
                        by=By.CLASS_NAME, value="job-card-list__title"
                    )
                    company = job.find_element(
                        by=By.CLASS_NAME, value="job-card-container__company-name"
                    )

                    if any(
                        company.text.upper().find(name.upper()) > -1
                        for name in premium_org_list
                    ):
                        organization_type = "Premium"

                    else:
                        organization_type = ""

                    job_location = job.find_element(
                        by=By.CLASS_NAME, value="job-card-container__metadata-item"
                    )
                    linkedin_job_link = (
                        job.find_element(
                            by=By.CLASS_NAME, value="artdeco-entity-lockup__title"
                        )
                        .find_element(by=By.CSS_SELECTOR, value="a")
                        .get_attribute("href")
                    )

                    job_title.click()

                    sleep(2)

                    try:
                        job_industry = job.find_element(
                            by=By.XPATH,
                            value="//li[@class='jobs-unified-top-card__job-insight']/span[contains(normalize-space(), 'employees')]",
                        ).get_attribute("innerHTML")

                        job_industry = bs(job_industry, features="html.parser").text

                        job_industry = job_industry.split("·")[1].strip()
                    except:
                        job_industry = "Not Mentioned"

                    # try:
                    #     skill_match = job.find_element(
                    #         by=By.XPATH,
                    #         value="//span[contains(normalize-space(), 'You have a preferred skill badge') or contains(normalize-space(), 'Your skills are a strong match for this job')]",
                    #     ).get_attribute("innerHTML")

                    #     skill_match = bs(
                    #         skill_match, features="html.parser"
                    #     ).text.strip()

                    # except:
                    #     skill_match = "Not Mentioned"

                    job_desc = job.find_element(
                        by=By.XPATH, value="//div[@id='job-details']"
                    ).get_attribute("innerHTML")

                    job_desc = bs(job_desc, features="html.parser").text.strip()

                    if any(
                        job_desc.find(check) > -1 for check in additional_filter_list
                    ):
                        new_row = pd.DataFrame(
                            {
                                "Job_ID": job_id,
                                "Job_Title": job_title.text,
                                "Organization": company.text,
                                "Organization_Type": organization_type,
                                "Job_Location": job_location.text,
                                "LinkedIn_Job_Link": linkedin_job_link,
                                "Job_Industy": job_industry,
                                # "Skill_Match": skill_match,
                                "Job_Description": job_desc,
                            },
                            dtype="str",
                            index=[0],
                        )
                        df = pd.concat([new_row, df.loc[:]]).reset_index(drop=True)

            try:
                next_page_button = self.driver.find_element(
                    by=By.XPATH,
                    value=f"//button[contains(@aria-label,'Page {current_page_number + 1}')]",
                )
                print(
                    f"Page {current_page_number} jobs details extraction complete. Moving to page number {current_page_number + 1}"
                )
                next_page_button.click()
                current_page_number = current_page_number + 1

            except:
                compression_opts = dict(
                    method="zip", archive_name=self.target_file_name + ".csv"
                )
                df.to_csv(
                    self.target_location + self.target_file_name + ".zip",
                    index=False,
                    compression=compression_opts,
                )
                print(f"Read all {self.total_results_count} jobs")
                break
