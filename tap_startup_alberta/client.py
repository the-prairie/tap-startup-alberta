"""REST client handling, including startup-albertaStream base class."""

import requests
import json
from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable

from flatten_json import flatten

from memoization import cached

from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.streams import RESTStream
from singer_sdk.authenticators import BasicAuthenticator


SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class StartupStream(RESTStream):
    """startup-alberta stream class."""
    
    rest_method = "POST"

    url_base = "https://api.dealroom.co/api/v2"

    records_jsonpath = "$.items[*]"  # Or override `parse_response`.
    
    max_offset = 25


    @property
    def http_headers(self) -> dict:
        """Return the http headers needed."""
        headers = {
            
            "authority": "api.dealroom.co",
            "content-type": "application/json",
            "origin": "https://ecosystem.startalberta.ca",
            "x-dealroom-app-id": self.config.get("app_id"),
            "x-requested-with": "XMLHttpRequest",
            "accept-encoding": "gzip, deflate, br"
            
        }

        return headers


    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:

        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}
        params["token"] = self.config.get("token")
        return params

    def prepare_request_payload(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Optional[dict]:
        

        """Prepare the data payload for the REST API request.

        By default, no payload will be sent (return None).
        """
        payload = {
            "fields":"id,angellist_url,appstore_app_id,client_focus,company_status,core_side_value,corporate_industries,create_date,crunchbase_url,employee_12_months_growth_delta,employee_12_months_growth_percentile,employee_12_months_growth_relative,employee_12_months_growth_unique,employee_3_months_growth_delta,employee_3_months_growth_percentile,employee_3_months_growth_relative,employee_3_months_growth_unique,employee_6_months_growth_delta,employee_6_months_growth_percentile,employee_6_months_growth_relative,employee_6_months_growth_unique,employees_chart,employees_latest,employees,entity_sub_types,facebook_url,founders_score_cumulated,founders,founders_top_university,founders_top_past_companies,fundings,fundings,growth_stage,has_strong_founder,has_super_founder,has_promising_founder,hq_locations,images,income_streams,industries,innovations,innovations_count,investments,investors,is_editorial,is_ai_data,is_from_traderegister,latest_revenue_enhanced,latest_valuation_enhanced,launch_month,launch_year,linkedin_url,lists_ids,matching_score,name,participated_events,past_founders_raised_10m,past_founders,path,playmarket_app_id,revenues,sdgs,service_industries,similarweb_12_months_growth_delta,similarweb_12_months_growth_percentile,similarweb_12_months_growth_relative,similarweb_12_months_growth_unique,similarweb_3_months_growth_delta,similarweb_3_months_growth_percentile,similarweb_3_months_growth_relative,similarweb_3_months_growth_unique,similarweb_6_months_growth_delta,similarweb_6_months_growth_percentile,similarweb_6_months_growth_relative,similarweb_6_months_growth_unique,similarweb_chart,sub_industries,tags,tagline,technologies,total_funding,total_jobs_available,trading_multiples,type,tech_stack,twitter_url,job_roles",
            "limit":25,
            "offset": next_page_token,
            "form_data": 
             {"must":{"filters":{"all_slug_locations":{"values":["alberta_1"],"execution":"and"}},"execution":"and"},
              "should":{"filters":{}},
              "must_not":{"growth_stages":["mature"],"company_type":["service provider","government nonprofit"],"tags":["outside tech"],"company_status":["closed"]}
              },
         "sort":"-last_funding_date"}
        
        return payload
    
    def get_next_page_token(
        self, response: requests.Response, previous_token: Optional[Any],
    ) -> Optional[Any]:
        """Return token identifying next page or None if all records have been read.

        Args:
            response: A raw `requests.Response`_ object.
            previous_token: Previous pagination reference.

        Returns:
            Reference value to retrieve next page.

        .. _requests.Response:
            https://docs.python-requests.org/en/latest/api/#requests.Response
        """
        previous_token = json.loads(response.request.body.decode())["offset"] or 0
        total_items = response.json()['total']
        
        if previous_token < total_items:
            return previous_token + self.max_offset
        else:
            return None




    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        # TODO: Parse response body and return a set of records.
        
        yield from extract_jsonpath(self.records_jsonpath, input=response.json())

    def post_process(self, row: dict, context: Optional[dict]) -> dict:
        """As needed, append or transform raw data to match expected structure."""
        #row = flatten(row)
        return row
