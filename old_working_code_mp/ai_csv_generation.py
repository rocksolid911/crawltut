# To run this code you need to install the following dependencies:
# pip install google-genai

import base64
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.types import HttpOptions

load_dotenv()
api_key = os.getenv("API_KEY")

def generate(md_content,output_file="output.json"):
    client = genai.Client(
        http_options=HttpOptions(api_version="v1"),
        api_key=api_key,
    )

    model = "gemini-2.5-flash-preview-05-20"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=md_content),
            ],
        ),
        types.Content(
            role="model",
            parts=[
                types.Part.from_text(text="""{
  \"candidate_name\": \"BISHNU PADA RAY\",
  \"party\": \"Bharatiya Janata Party (BJP)\",
  \"constituency\": \"ANDAMAN AND NICOBAR ISLANDS\",
  \"father_or_husband_name\": \"Late Ramashis Ray\",
  \"age\": 73,
  \"education\": \"Graduate, Bachelor of Commerce (B.Com Hons.) from University of Calcutta, Year 1973\",
  \"profession_self\": \"Social Service\",
  \"profession_spouse\": \"Pensioner\",
  \"criminal_cases\": 0,
  \"assets_total_inr\": 27439170,
  \"liabilities_total_inr\": 302788,
  \"income_tax_details\": {
    \"self\": {
      \"pan_given\": \"Y\",
      \"income_by_financial_year\": {
        \"2022-2023\": 537210,
        \"2021-2022\": 824760,
        \"2020-2021\": 537730,
        \"2019-2020\": 584176,
        \"2018-2019\": 608878
      }
    },
    \"spouse\": {
      \"pan_given\": \"Y\",
      \"income_by_financial_year\": {
        \"2022-2023\": 655700,
        \"2021-2022\": 643700,
        \"2020-2021\": 545740,
        \"2019-2020\": 558010,
        \"2018-2019\": 576700
      }
    },
    \"huf\": {
      \"pan_given\": \"N\",
      \"income_by_financial_year\": {
        \"None\": 0
      }
    },
    \"dependent1\": {
      \"pan_given\": \"N\",
      \"income_by_financial_year\": {
        \"None\": 0
      }
    },
    \"dependent2\": {
      \"pan_given\": \"N\",
      \"income_by_financial_year\": {
        \"None\": 0
      }
    },
    \"dependent3\": {
      \"pan_given\": \"N\",
      \"income_by_financial_year\": {
        \"None\": 0
      }
    }
  },
  \"movable_assets\": {
    \"self\": {
      \"cash_inr\": 30000,
      \"bank_deposits_inr\": 1526559,
      \"bonds_debentures_shares_inr\": 14700,
      \"nss_postal_savings_inr\": 0,
      \"lic_other_insurance_inr\": 666665,
      \"personal_loans_advance_given_inr\": 0,
      \"motor_vehicles_inr\": 670000,
      \"jewellery_inr\": 0,
      \"other_assets_inr\": 0,
      \"gross_total_value_inr\": 2909477
    },
    \"spouse\": {
      \"cash_inr\": 40000,
      \"bank_deposits_inr\": 10695,
      \"bonds_debentures_shares_inr\": 117000,
      \"nss_postal_savings_inr\": 0,
      \"lic_other_insurance_inr\": 639610,
      \"personal_loans_advance_given_inr\": 0,
      \"motor_vehicles_inr\": 0,
      \"jewellery_inr\": 1500000,
      \"other_assets_inr\": 0,
      \"gross_total_value_inr\": 2307306
    }
  },
  \"immovable_assets\": {
    \"self\": {
      \"agricultural_land_inr\": 0,
      \"non_agricultural_land\": {
        \"description\": \"Veer Savarkar Coop. Housing Society Teylarabad Project No. 1, Plot No. 7\",
        \"area_sq_mtr\": 540,
        \"inherited\": \"N\",
        \"purchase_date\": \"1992-07-15\",
        \"purchase_cost_inr\": 25000,
        \"development_cost_inr\": 0,
        \"current_market_value_inr\": 3000000
      },
      \"commercial_buildings_inr\": 0,
      \"residential_buildings\": {
        \"description\": \"Landed Property with Shed at Vill. Phoenix Bay, Sy. No. 1312/2/2\",
        \"total_area_sqft\": 3000,
        \"built_up_area_sqft\": 1060,
        \"inherited\": \"N\",
        \"purchase_date\": \"1993-01-01\",
        \"purchase_cost_inr\": 100000,
        \"development_cost_inr\": 2755877,
        \"current_market_value_inr\": 7788527
      },
      \"others_inr\": 0,
      \"total_current_market_value_inr\": 10788527
    },
    \"spouse\": {
      \"agricultural_land_inr\": 0,
      \"non_agricultural_land\": {
        \"description\": \"Veer Savarkar Coop. Housing Society Teylarabad Project No. 2, Plot No. 6\",
        \"area_sq_mtr\": 540,
        \"inherited\": \"N\",
        \"purchase_date\": \"1992-07-15\",
        \"purchase_cost_inr\": 25000,
        \"development_cost_inr\": 0,
        \"current_market_value_inr\": 3000000
      },
      \"commercial_buildings_inr\": 0,
      \"residential_buildings\": {
        \"description\": \"Landed Property with Double Storied Semi-RCC House at Aberdeen Village, Sy. No. 91\",
        \"total_area_sqft\": 1820,
        \"built_up_area_sqft\": 1800,
        \"inherited\": \"N\",
        \"purchase_date\": \"0000-00-00\",
        \"purchase_cost_inr\": 0,
        \"development_cost_inr\": 4702860,
        \"current_market_value_inr\": 8433860
      },
      \"others_inr\": 0,
      \"total_current_market_value_inr\": 11433860
    }
  },
  \"liabilities_details\": {
    \"self\": {
      \"loans_from_banks_fis_inr\": 302788,
      \"loans_due_to_individual_entity_inr\": 0,
      \"any_other_liability_inr\": 0,
      \"grand_total_of_liabilities_inr\": 302788
    },
    \"spouse\": {
      \"loans_from_banks_fis_inr\": 0,
      \"loans_due_to_individual_entity_inr\": 0,
      \"any_other_liability_inr\": 0,
      \"grand_total_of_liabilities_inr\": 0
    },
    \"government_dues\": {
      \"dues_govt_accommodation_inr\": 0,
      \"dues_water_supply_inr\": 0,
      \"dues_electricity_supply_inr\": 0,
      \"dues_telephones_inr\": 0,
      \"dues_transport_inr\": 0,
      \"income_tax_dues_inr\": 0,
      \"wealth_tax_dues_inr\": 0,
      \"service_tax_dues_inr\": 0,
      \"property_tax_dues_inr\": 0,
      \"sales_tax_dues_inr\": 0,
      \"gst_dues_inr\": 0,
      \"any_other_dues_inr\": 0,
      \"grand_total_of_all_govt_dues_inr\": 0
    },
    \"other_liabilities_in_dispute_inr\": 0
  },
  \"sources_of_income\": {
    \"self\": \"Ex-Member of Parliament Pension, LIC Pension Policy\",
    \"spouse\": \"Govt. Pensioner, LIC Pension Policy\",
    \"dependent\": \"NA\"
  },
  \"contracts\": {
    \"entered_by_candidate\": \"NA\",
    \"entered_by_spouse\": \"NA\",
    \"entered_by_dependent\": \"NA\",
    \"entered_by_huf_trust\": \"NA\",
    \"entered_by_partnership_firms\": \"NA\",
    \"entered_by_private_companies\": \"Nil\"
  }
}"""),
            ],
        ),
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""i have provided the candidate details in markdown and a reference json format.extract the candidate 
                profile details from the markdown and convert it to json format as per the reference json format provided."""),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        thinking_config = types.ThinkingConfig(
            thinking_budget=0,
        ),
        response_mime_type="application/json",
    )

    with open(output_file, "w") as f:
        for chunk in client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=generate_content_config,
        ):
            # print(chunk.text, end="")
            f.write(chunk.text)

