from marshmallow_sqlalchemy import ModelSchema, field_for
from tyrenet_orm import models


class CustomerSchema(ModelSchema):
    class Meta:
        model = models.Customer


class CreditSafeSchema(ModelSchema):

    class Meta:
        model = models.Customer


class StockLineAnalysisSchema(ModelSchema):
    quantity = field_for(models.StockLineAnalysis, 'quantity', as_string=True)

    class Meta:
        model = models.StockLineAnalysis


class ManufacturerSchema(ModelSchema):
    class Meta:
        model = models.Manufacturer
