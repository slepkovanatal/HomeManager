import os

from pydantic import BaseModel

from providers.ah_config import get_anonymous_access_token, search_products, extract_largest_images
from services.openai_client import client, create_file
from services.product_image_service import ProductImageService


class ProductInfoCollector:
    THRESHOLD = 0.75
    MAX_DIFFERENCE = 0.02

    def __init__(self):
        self._ah_access_token = get_anonymous_access_token()

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

        class SalesUnitSize(BaseModel):
            sales_unit_size: int

        resp_size = client.responses.parse(
            model="gpt-4o",
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text":
                            "Find sales unit size on provided image"},
                        {"type": "input_image", "file_id": product_photo_file_id}
                    ]
                }
            ],
            text_format=SalesUnitSize
        )

        size = resp_size.output_parsed.sales_unit_size
        print(size)
        #TODO add a validation to determine whether the keywords already include this information
        keywords.append(str(size))

        return keywords

    @staticmethod
    def keywords_to_query(keywords: list[str]) -> str:
        query = ""
        for i, kw in enumerate(keywords):
            query += f"'{kw}'"
            if i < len(keywords) - 1:
                query += ", "
        return query

    def get_all_relevant_products(self):
        keywords = self.extract_keywords()
        query = self.keywords_to_query(keywords)

        relevant_products_data = search_products(query)
        candidates_info = extract_largest_images(relevant_products_data)
        candidates = self.product_image_service.get_candidates_similarity(candidates_info)
        return candidates

    def execute(self) -> list[str]:
        products_info = self.get_all_relevant_products()
        sorted_products_info = sorted(products_info, key=lambda x: x[1], reverse=True)

        suitable_products = []
        if 0 < len(sorted_products_info):
            max_similarity = sorted_products_info[0][1]
            for info in sorted_products_info:
                if info[1] < self.THRESHOLD or self.MAX_DIFFERENCE < max_similarity - info[1]:
                    break
                suitable_products.append(info[0])

        return suitable_products
