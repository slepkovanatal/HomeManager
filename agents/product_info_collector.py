import os

from pydantic import BaseModel

from providers.ah_config import get_anonymous_access_token, extract_products_data
from services.openai_client import client, create_file
from services.product_image_service import ProductImageService


class ProductInfoCollector:
    THRESHOLD = 0.75
    MAX_DIFFERENCE = 0.02

    def __init__(self):
        self.product_file_path = os.path.join('tmp', 'product_photo.jpg')
        self.product_image_service = ProductImageService(self.product_file_path)

    def extract_keywords(self) -> list[str]:
        class ProductDescription(BaseModel):
            keywords: list[str]

        product_photo_file_id = create_file(self.product_file_path)

        resp = client.responses.parse(
            model="gpt-4o",
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text":
                            "Find keywords on image related to the item."
                            "Sort them by importance from the most important to the least."},
                        {"type": "input_image", "file_id": product_photo_file_id}
                    ]
                }
            ],
            text_format=ProductDescription
        )

        description = resp.output_parsed
        keywords = description.keywords
        print(keywords)

        # class SalesUnitSize(BaseModel):
        #     sales_unit_size: int
        #
        # resp_size = client.responses.parse(
        #     model="gpt-4o",
        #     input=[
        #         {
        #             "role": "user",
        #             "content": [
        #                 {"type": "input_text", "text":
        #                     "Find sales unit size on provided image"},
        #                 {"type": "input_image", "file_id": product_photo_file_id}
        #             ]
        #         }
        #     ],
        #     text_format=SalesUnitSize
        # )
        #
        # size = resp_size.output_parsed.sales_unit_size
        # print(size)
        # #TODO add a validation to determine whether the keywords already include this information
        # keywords.append(str(size))

        return keywords

    @staticmethod
    def keywords_to_query(keywords: list[str]) -> str:
        query = ""
        for i, kw in enumerate(keywords):
            query += f"'{kw}'"
            if i < len(keywords) - 1:
                query += ", "
        return query

    def get_all_relevant_products_via_ah_api(self, keywords: list[str]):
        query = self.keywords_to_query(keywords)

        candidates_data = extract_products_data(query)
        candidates = self.product_image_service.get_candidates_similarity(candidates_data)
        return candidates

    def get_all_relevant_products_via_ai(self, keywords: list[str]):
        prompt = (f"Find an item that matches the description {keywords} on the website ah.nl "
                  f"using the search tool.")
        resp = client.responses.create(model="gpt-4o",
                                       input=[{
                                           "role": "user",
                                           "content": [{
                                               "type": "input_text",
                                               "text": prompt
                                           }]
                                       }],
                                       tools=[{
                                           "type": "web_search",
                                           "user_location": {
                                               "type": "approximate",
                                               "country": "NL"
                                           }
                                       }]
                                       )

        product_urls = set()
        for out in resp.output:
            if out.type == "message":
                for annotation in out.content[0].annotations:
                    product_urls.add(annotation.url)

        candidates_data = extract_products_data(list(product_urls))
        candidates = self.product_image_service.get_candidates_similarity(candidates_data)

        return candidates

    def search_products(self) -> list[(str, float)]:
        def validate_products_data(products_data) -> bool:
            if 0 < len(products_data) and self.THRESHOLD < max(products_data, key=lambda x: x[1])[1]:
                return True
            return False

        keywords = self.extract_keywords()
        products_data = self.get_all_relevant_products_via_ah_api(keywords)
        if not validate_products_data(products_data):
            keywords = self.extract_keywords()
            products_data = self.get_all_relevant_products_via_ah_api(keywords)

        if not validate_products_data(products_data):
            products_data = self.get_all_relevant_products_via_ai(keywords)
            if len(products_data) == 0:
                products_data = self.get_all_relevant_products_via_ai(keywords)

            if 0 < len(products_data):
                max_suitability = max(products_data, key=lambda x: x[1])
                if max_suitability[1] < self.THRESHOLD:
                    keywords = self.extract_keywords()
                    products_data = self.get_all_relevant_products_via_ai(keywords)
        return products_data

    def execute(self) -> list[dict]:
        products = self.search_products()

        suitable_products = []
        if 0 < len(products):
            sorted_products_info = sorted(products, key=lambda x: x[1], reverse=True)

            max_similarity = sorted_products_info[0][1]
            for info in sorted_products_info:
                if info[1] < self.THRESHOLD or self.MAX_DIFFERENCE < max_similarity - info[1]:
                    break
                suitable_products.append(info[0])

        return suitable_products
