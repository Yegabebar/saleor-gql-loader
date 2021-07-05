import json
import requests


def graphql_request(query, variables={}, headers={}, endpoint="http://192.168.1.61:8000/graphql/"):
    json_content = {'query': query}
    if len(variables) != 0:
        json_content.update({'variables': variables})

    print(json_content)
    response = requests.post(
        endpoint,
        headers=headers,
        json=json_content
    )

    parsed_response = json.loads(response.text)
    if response.status_code != 200:
        raise Exception("{message}\n extensions: {extensions}".format(
            **parsed_response["errors"][0]))
    else:
        return parsed_response


class ETLDataRequester:

    def __init__(self, auth_token, endpoint_url="http://192.168.1.61:8000/graphql/"):
        """initialize the `DataRequester` with an auth_token and an url endpoint.

        Parameters
        ----------
        auth_token : str
            token used to identify called to the graphQL endpoint.
        endpoint_url : str, optional
            the graphQL endpoint to be used , by default "http://localhost:8000/graphql/"
        """
        self.headers = {"Authorization": "JWT {}".format(auth_token)}
        self.endpoint_url = endpoint_url

    def get_customers(self, number=20):
        return f"""query customers($first: Int = {number}){{
                  customers(first: $first){{
                    pageInfo{{
                      hasPreviousPage
                      hasNextPage
                        startCursor
                    }}
                    edges{{
                      node{{
                        id
                        firstName
                        lastName
                        email
                      }}
                    }}
                  }}
                }}"""

    def get_products(self,
                     number_of_results=100,
                     after_id="",
                     t_size=100,
                     img_size=100,
                     search_string="",
                     sort_method="",
                     direction="DESC"
                     ):
        variables_filter = ""
        if after_id != "":
            variables_filter = f'last: {number_of_results}'
        else:
            variables_filter = f'last: {number_of_results} after: "{after_id}"'
        if search_string != "":
            variables_filter += f'filter: {{search:"{search_string}"}}'

        if sort_method != "":
            if direction != "DESC":
                direction = "ASC"
            variables_filter += f'sortBy: {{field: {sort_method}, direction: {direction}}}'

        query = f"""query {{
                  products({variables_filter}) {{
                    edges {{
                      node {{
                        id
                        name
                         pricing{{
                          priceRange{{
                            start{{
                              currency
                              tax{{
                                amount
                                currency
                              }}
                              net{{
                                amount
                                currency
                              }}
                              currency
                            }}
                            stop{{
                              currency
                              tax{{
                                amount
                                currency
                              }}
                              net{{
                                amount
                                currency
                              }}
                            }}
                          }}
                        }}
                        thumbnail(size: {t_size}) {{
                            url
                            alt
                        }}
                        images {{
                          url(size: {img_size})
                          alt
                        }}
                      }}
                    }}
                  }}
                }}"""
        return graphql_request(query, self.headers)

    def get_product_by_id(self,
                          product_id,
                          size):
        query = f"""query {{
                  product(id: "{product_id}") {{
                    id
                    name
                    description
                    productType
                    pricing{{
                          priceRange{{
                            start{{
                              currency
                              tax{{
                                amount
                                currency
                              }}
                              net{{
                                amount
                                currency
                              }}
                              currency
                            }}
                            stop{{
                              currency
                              tax{{
                                amount
                                currency
                              }}
                              net{{
                                amount
                                currency
                              }}
                            }}
                          }}
                        }}
                    thumbnail(size: {size}) {{
                            url
                            alt
                        }}
                        images {{
                          url(size: {size})
                          alt
                        }}
                  }}
                }}"""
        return graphql_request(query, self.headers)
