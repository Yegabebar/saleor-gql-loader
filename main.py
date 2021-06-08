from saleor_gql_loader import ETLDataLoader, utils


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


def main():
    # create a default warehouse
    # warehouse_id = etl_data_loader.create_warehouse()
    # create a default shipping zone associated
    """shipping_zone_id = etl_data_loader.create_shipping_zone(addWarehouses=["79891a8c-7e28-48fd-8472-28edb13467a2"])
    print(shipping_zone_id)"""

    products = [
        {
            "name": "tea d",
            "description": "description for tea a",
            "category": "green tea",
            "price": 5.5,
            "strength": "medium"
        },
        {
            "name": "tea e",
            "description": "description for tea b",
            "category": "black tea",
            "price": 10.5,
            "strength": "strong"
        },
        {
            "name": "tea f",
            "description": "description for tea c",
            "category": "green tea",
            "price": 9.5,
            "strength": "light"
        }
    ]
    # authentication is managed here
    response = utils.graphql_request(get_auth_query())
    auth_token = response['data']['tokenCreate']['token']
    etl_data_loader = ETLDataLoader(auth_token)

    # add basic sku to products
    for i, product in enumerate(products):
        product["sku"] = "{:05}-00".format(i)

    # does not take in account which attributes exists or not
    # TODO: do a graphql request to check if the given attribute already exists or not in saleor.
    # if not, it will create it:
    # create the strength attribute
    strength_attribute_id = etl_data_loader.create_attribute(name="strength")
    unique_strength = set([product['strength'] for product in products])
    for strength in unique_strength:
        etl_data_loader.create_attribute_value(strength_attribute_id, name=strength)

    # will be used if we want to support product variants
    # create another quantity attribute used as variant:
    qty_attribute_id =  etl_data_loader.create_attribute(name="qty")
    unique_qty = {"100g", "200g", "300g"}
    for qty in unique_qty:
        etl_data_loader.create_attribute_value(qty_attribute_id, name=qty)

    # does not take in account if product types exist or not
    # TODO: do a graphql request to check if the given product type already exists or not in saleor.
    # create a product type: tea
    product_type_id = etl_data_loader.create_product_type(name="tea",
                                                          hasVariants=True,
                                                          productAttributes=[strength_attribute_id],
                                                          variantAttributes=[qty_attribute_id])

    # does not take in account if categories exist or not
    # TODO: do a graphql request to check if the given category already exists or not in saleor.
    # create categories
    unique_categories = set([product['category'] for product in products])

    cat_to_id = {}
    for category in unique_categories:
        cat_to_id[category] = etl_data_loader.create_category(name=category)

    # create products and store id
    for i, product in enumerate(products):
        product_id = etl_data_loader.create_product(product_type_id,
                                                    name=product["name"],
                                                    description=product["description"],
                                                    basePrice=product["price"],
                                                    sku=product["sku"],
                                                    category=cat_to_id[product["category"]],
                                                    attributes=[{"id": strength_attribute_id, "values": [product["strength"]]}],
                                                    isPublished=True)
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


if __name__ == '__main__':
    main()
