class ProductPagesException(Exception):
    pass


class ReleaseNotFoundException(ProductPagesException):
    pass


class TaskNotFoundException(ProductPagesException):
    pass
