class BikeRentalError(Exception): pass
class ValidationError(BikeRentalError): pass
class EntityNotFoundError(BikeRentalError): pass
class DuplicateEntityError(BikeRentalError): pass
class BikeUnavailableError(BikeRentalError): pass
class RentalAlreadyClosedError(BikeRentalError): pass
