# WARNING: Do not edit by hand, this file was generated by Crank:
#
#   https://github.com/gocardless/crank
#

class Customer(object):
    """A thin wrapper around a customer, providing easy access to its
    attributes.

    Example:
      customer = client.customers.get()
      customer.id
    """

    def __init__(self, attributes, api_response):
        self.attributes = attributes
        self.api_response = api_response

    @property
    def address_line1(self):
        return self.attributes.get('address_line1')
  

    @property
    def address_line2(self):
        return self.attributes.get('address_line2')
  

    @property
    def address_line3(self):
        return self.attributes.get('address_line3')
  

    @property
    def city(self):
        return self.attributes.get('city')
  

    @property
    def company_name(self):
        return self.attributes.get('company_name')
  

    @property
    def country_code(self):
        return self.attributes.get('country_code')
  

    @property
    def created_at(self):
        return self.attributes.get('created_at')
  

    @property
    def danish_identity_number(self):
        return self.attributes.get('danish_identity_number')
  

    @property
    def email(self):
        return self.attributes.get('email')
  

    @property
    def family_name(self):
        return self.attributes.get('family_name')
  

    @property
    def given_name(self):
        return self.attributes.get('given_name')
  

    @property
    def id(self):
        return self.attributes.get('id')
  

    @property
    def language(self):
        return self.attributes.get('language')
  

    @property
    def metadata(self):
        return self.attributes.get('metadata')
  

    @property
    def postal_code(self):
        return self.attributes.get('postal_code')
  

    @property
    def region(self):
        return self.attributes.get('region')
  

    @property
    def swedish_identity_number(self):
        return self.attributes.get('swedish_identity_number')
  


  

  

  

  

  

  

  

  

  

  

  

  

  

  

  

  

  

