import itertools
import time

from src.scraper import JobData


def test_webdriver():
    job_obj = JobData()
    job_obj.setup_webdriver()
    job_obj.driver.quit()


def test_linkedin_url():
    job_title_list = ["", "Data Scientist"]
    job_location_list = ["", "California"]
    distance_list = ["", 100]
    company_list = ["", "Amazon"]

    job_obj = JobData()
    job_obj.setup_webdriver()

    for job_title, job_location, distance, company in itertools.product(job_title_list, job_location_list,
                                                                        distance_list, company_list):
        job_obj.update_attributes(job_title=job_title, job_location=job_location, distance=distance,
                                  company=company)
        url = job_obj.get_linkedin_url()
        job_obj.driver.get(url)

        assert type(url) == str

        time.sleep(1)

    job_obj.driver.quit()


def test_scraper():
    job_title = "Software Engineer"
    job_location = "Raleigh"
    distance = 20
    company = ""
    number_jobs = 10
    job_obj = JobData(job_title=job_title, job_location=job_location, distance=distance, company=company,
                      number_jobs=number_jobs)
    job_obj.scrape_data()


def test_scraper_zero_jobs():
    number_jobs = 0
    job_obj = JobData(number_jobs=number_jobs)
    job_obj.scrape_data()


def test_update_attributes():
    job_title = "Software Engineer"
    job_location = "Raleigh"
    distance = 20
    company = ""
    number_jobs = 10

    job_obj = JobData()
    job_obj.update_attributes(job_title=job_title, job_location=job_location, distance=distance, company=company,
                              number_jobs=number_jobs)

    assert job_obj.job_title == job_title
    assert job_obj.job_location == job_location
    assert job_obj.distance == distance
    assert job_obj.company == company
    assert job_obj.number_jobs == number_jobs