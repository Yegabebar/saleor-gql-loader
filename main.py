import csv
import sys

from saleor_gql_loader import ETLDataLoader, utils, ETLDataRequester


# TODO: Move the authentication query in the package utils
def get_auth_query():
    return """fragment
                User
                on
                User
                {
                    id
                    email
                    firstName
                    lastName
                    userPermissions{
                            code
                            name
                        }
                    avatar{
                            url
                        }
                }
                mutation
                TokenAuth($email: String = "admin@admin.admin", $password: String = "P455w0rd") {
                    tokenCreate(email: $email, password: $password) {
                        errors: accountErrors {
                            field
                            message
                        }
                        csrfToken
                        token
                        user
                        {
                            ...User
                        }
                    }
                }"""


def get_attribute_by_name(name):
    return f"""{{
                attributes(filter:{{search:"{name}"}} first: 1){{
                      edges{{
                        node{{
                                id
                          name
                        }}
                      }}
                    }}
                    }}"""


def import_mode(etl_data_loader, product_csv):
    # create a default warehouse
    # warehouse_id = etl_data_loader.create_warehouse()
    # create a default shipping zone associated
    """shipping_zone_id = etl_data_loader.create_shipping_zone(addWarehouses=["79891a8c-7e28-48fd-8472-28edb13467a2"])
    print(shipping_zone_id)"""

    # products = [
    #     {
    #         "name": "tea n",
    #         "description": "description for tea a",
    #         "category": "green tea",
    #         "price": 5.5,
    #         "strength": "medium"
    #     },
    #     {
    #         "name": "tea o",
    #         "description": "description for tea b",
    #         "category": "black tea",
    #         "price": 10.5,
    #         "strength": "strong"
    #     },
    #     {
    #         "name": "tea p",
    #         "description": "description for tea c",
    #         "category": "green tea",
    #         "price": 9.5,
    #         "strength": "light"
    #     }
    # ]

    # TODO: Use our csv file to create new products
    products = []
    print("path to csv file: ", product_csv)
    with open(product_csv, newline='') as file:
        csv_content = csv.DictReader(file, fieldnames=["name", "category", "price", "pros", "desc", "ingredients",
                                                       "how_to_use", "pictures"], delimiter=';', quotechar='|')
        for row in csv_content:
            product = {"name": row['name'],
                       "type": row['category'],
                       # The CSV file has makeup as category but in this script we want it to be a type
                       "category": "base",
                       # Will need to pass a product type either from the CSV or as an exec argument
                       "price": row['price'],
                       "pros": row['pros'],
                       "desc": row['desc'],
                       "ingredients": row['ingredients'],
                       "how_to_use": row['how_to_use'],
                       "pictures": row['pictures']
                       }
            products.append(product)

    # add basic sku to products
    for i, product in enumerate(products):
        product["sku"] = "{:05}-00".format(i)

    # BASE
    # does not take in account if categories exist or not
    # TODO: do a graphql request to check if the given category already exists or not in saleor.
    # create categories
    unique_categories = set([product['category'] for product in products])
    print("UNIQUE CATEGORIES: ", unique_categories)
    category_id_dict = {}
    for category in unique_categories:
        category_id_dict[category] = etl_data_loader.create_category(name=category)

    # does not take in account which attributes exists or not
    # TODO: do a graphql request to check if the given attribute already exists or not in saleor.
    # if not, it will create it:
    # create the strength attribute
    """strength_attribute_id = etl_data_loader.create_attribute(name="strength")
    unique_strength = set([product['strength'] for product in products])
    for strength in unique_strength:
        etl_data_loader.create_attribute_value(strength_attribute_id, name=strength)"""

    # MAKEUP
    # does not take in account if product types exist or not
    # TODO: do a graphql request to check if the given product type already exists or not in saleor.
    # create the product types found in the CSV file
    unique_types = set([product['type'] for product in products])
    print("UNIQUE TYPES: ", unique_types)
    product_type_ids = {}
    for new_type in unique_types:
        product_type_id = etl_data_loader.create_product_type(name=new_type,
                                                              hasVariants=False,
                                                              # productAttributes=[strength_attribute_id],
                                                              )
        product_type_ids.update({new_type: product_type_id})

    """# will be used if we want to support product variants
    # create another quantity attribute used as variant:
    qty_attribute_id = etl_data_loader.create_attribute(name="qty")
    unique_qty = {"100g", "200g", "300g"}
    for qty in unique_qty:
        etl_data_loader.create_attribute_value(qty_attribute_id, name=qty)"""

    current_product_type_id = ""
    current_category_id = ""
    # create products and store id
    for i, product in enumerate(products):
        print(len(product_type_ids))
        if len(product_type_ids) > 1:
            for type_id in product_type_ids:
                current_product_type_id = [id_ for id_ in type_id if type_id == product['name']]
                print(current_product_type_id)
                break
        else:
            current_product_type_id = [id_ for id_ in product_type_ids][0]

        print(len(category_id_dict))
        if len(category_id_dict) > 1:
            for category in category_id_dict:
                current_category_id = [id_ for id_ in category if category == product['category']]
                print(current_category_id)
                break
        else:
            current_category_id = [id_ for id_ in category_id_dict][0]

        product_id = etl_data_loader.create_product(current_product_type_id,
                                                    name=product["name"],
                                                    description=product["desc"],
                                                    basePrice=product["price"],
                                                    sku=product["sku"],
                                                    category=current_category_id,
                                                    # attributes=[{"id": strength_attribute_id, "values": [product["strength"]]}],
                                                    isPublished=True

                                                    )
        products[i]["id"] = product_id

    """# create some variant for each product:
    for product in products:
        for i, qty in enumerate(unique_qty):
            variant_id = etl_data_loader.create_product_variant(product_id,
                                                                sku=product["sku"].replace("-00", "-1{}".format(i+1)),
                                                                attributes=[{"id": qty_attribute_id, "values": [qty]}],
                                                                costPrice=product["price"],
                                                                weight=0.75,
                                                                stocks=[{"warehouse": warehouse_id, "quantity": 15}])"""


def request_mode(etl_data_requester):
    print(etl_data_requester.get_products())


if __name__ == '__main__':
    # Variables initialization
    import_mode_activated = False
    reachable = False
    index_for_csv_arg = 0
    path_to_csv = ""
    csv_file = ""
    # Check if the script will be run in import mode or not
    for index, arg in enumerate(sys.argv):
        if arg == "-i":
            # if an argument -i is found, get the next argument (which should be a csv path)
            try:
                path_to_csv = sys.argv[index + 1]
                index_for_csv_arg = index + 1
                import_mode_activated = True
            except Exception as e:
                print("Please provide a path to a csv file for -i: ", e)

    # authentication is managed here
    response = utils.graphql_request(get_auth_query())
    auth_token = response['data']['tokenCreate']['token']

    if import_mode_activated:
        if ".csv" in sys.argv[index_for_csv_arg]:
            try:
                csv_file = open(path_to_csv)
                if len(csv_file.read()) != 0:
                    edl = ETLDataLoader(auth_token)
                    reachable = True
                else:
                    print("The provided CSV file is empty")
                csv_file.close()

            except Exception as e:
                print("The file could not be opened: ", e)
            if reachable:
                print("Script executed in import mode")
                import_mode(edl, path_to_csv)
        else:
            print("Please provide a valid path to a CSV file")

    if not import_mode:
        # if no import argument found, the script will be executed in request mode
        edr = ETLDataRequester(auth_token)
        request_mode(edr)
