import datetime


class RoyalMailBody:
    def __init__(self, shipment_type):
        self.receipient = None
        self.address = None
        self.service = None
        self.shipping_date = None
        self._check_ship_type(shipment_type)
        self.sender_reference = None
        self.department_reference = None
        self.customer_reference = None
        self.items = []
        self.item_count = len(self.items)
        self.safe_place = None

    def return_domestic_body(self):
        """
        build domestic body from items
        :return:
        """

        domestic_body = {
            'shipmentType': self.shipment_type,
            'service': self.service,
            'shippingDate': self.shipping_date,
            'items': self.items,
            'recipientContact': self.receipient,
            'recipientAddress': self.address,
            'senderReference': self.sender_reference,
            'departmentReference': self.department_reference,
            'customerReference': self.customer_reference,
            'safePlace': self.safe_place
        }

        return domestic_body

    def return_domestic_update_boy(self):
        """
        build domestic body from items
        :return:
        """

        domestic_body = {
            'service': self.service,
            'shippingDate': self.shipping_date,
            'recipientContact': self.receipient,
            'recipientAddress': self.address,
            'senderReference': self.sender_reference,
            'departmentReference': self.department_reference,
            'customerReference': self.customer_reference,
            'safePlace': self.safe_place
        }

        return domestic_body

    @staticmethod
    def remove_none_values(iterable):
        """
        take out values of None by removing the key
        :param iterable:
        :return: dictionary
        """

        new_dict = {k: v for k, v in iterable.items() if v is not None}

        return new_dict

    def _check_ship_type(self, shipment_type):
        if shipment_type.lower() != 'delivery':
            # TODO: Find out the other options here!
            raise Exception('Sorry, only delivery supported at the moment')
        else:
            self.shipment_type = shipment_type.lower()

    def add_ship_date(self, date_obj=None):
        """
        take a datetime object and format it to royal mails Y-m-d format
        :param date_obj:
        :return:
        """
        if date_obj is None:
            date_obj = datetime.datetime.today()
        self.shipping_date = datetime.datetime.strftime(date_obj, '%Y-%m-%d')

    def add_service(self, format=None, occurrence=None, offering=None, _type=None, signature=None, enhancements=None):
        if not isinstance(enhancements, list):
            enhancements = [enhancements]

        service = {
            "format": format,
            "occurrence": occurrence,
            "offering": offering,
            "type": _type,
            "signature": signature,
            "enhancements": enhancements
            }

        self.service = service

    def add_receipient_contact(self, name, email, complementary_name=None, telephone=None):
        receipient = {
            "name": name,
            "complementaryName": complementary_name,
            "telephoneNumber": telephone,
            "email": email
        }

        # receipient = self.remove_none_values(receipient)
        self.receipient = receipient

    def add_items(self, number, weight, unit_of_measure):
        items = [{
            "count": number,
            "weight": {
                "unitOfMeasure": unit_of_measure,
                "value": weight
            },
        }]

        self.items = items

    def add_receipient_address(self, address_line1, post_town, county, postcode, country, building_name=None,
                               building_number=None, address_line2=None, address_line3=None):
        address = {
            "buildingName": building_name,
            "buildingNumber": building_number,
            "addressLine1": address_line1,
            "addressLine2": address_line2,
            "addressLine3": address_line3,
            "postTown": post_town,
            "county": county,
            "postCode": postcode,
            "country": country
        }

        # address = self.remove_none_values(address)
        self.address = address


