from datetime import datetime

from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Integer,
                        Numeric, String, create_engine)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Network(Base):
    __table_args__ = {'schema': 'CamShared'}
    __tablename__ = 'Network'

    id = Column('NetworkId', Integer, primary_key=True)
    network_code = Column(String(1))


class Customer(Base):
    __table_args__ = {'schema': 'CamShared'}
    __tablename__ = 'Customer'

    id = Column('CustomerId', Integer, primary_key=True)
    customer_code = Column('CustomerCode', String(50))
    customer_name = Column('CustomerName', String(100))
    company_reg_no = Column('CompanyRegNo', String(30))
    customer_level_type = Column('CustomerLevelType', Integer)
    external_id = Column('ExternalId', String(50))
    deleted_date = Column('DeletedDate', DateTime)
    status = Column('AccountStatusId', Integer)


class CustomerNetwork(Base):
    __table_args__ = {'schema': 'CamShared'}
    __tablename__ = 'CustomerNetwork'

    id = Column('CustomerNetworkId', Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey(Customer.id))
    network_id = Column(Integer, ForeignKey(Network.id))
    customer_network_code = Column(String(15))


class CreditRating(Base):
    __table_args__ = {'schema': 'Tyrenet'}
    __tablename__ = 'CreditRating'

    customer_id = Column(Integer, ForeignKey(Customer.id), primary_key=True)
    valid_from = Column(DateTime, primary_key=True, default=datetime.now())
    external_id = Column(String(50))
    valid_until = Column(DateTime)
    credit_limit = Column(Numeric(scale=12, precision=2))
    credit_rating = Column(String(1))
    credit_rating_pct = Column(Integer)
    credit_rating_desc = Column(String(50))


class Manufacturer(Base):
    __table_args__ = {'schema': 'CamShared'}
    __tablename__ = 'Manufacturer'

    id = Column('ManufacturerID', Integer, primary_key=True)
    manufacturer_code = Column('ManufacturerCode', String(50))
    manufacturer_description = Column('ManufacturerDesc', String(30))
    deleted_date = Column('DeletedDate', DateTime)
    external_id = Column('ExternalId', String(50))


class StockLineAnalysis(Base):
    __tablename__ = 'StockLineAnalysiscached'

    id = Column('tuid', String(20), primary_key=True)
    allocated_date = Column('ALLOCATEDDATE', DateTime)
    breakdown_location = Column('BreakdownLocationNotes', String(8000))
    company_code = Column('COCODE', String(8))
    company_description = Column('CONAME', String(35))
    invoice_number = Column('INVNUM', String(10))
    invoice_date = Column('INVDATE', DateTime)
    manufacturer_code = Column('MANUFACTURER', String(2))
    manufacturer_description = Column('ManufacturerDesc', String(30))
    old_advice_number = Column('OLDADVICENUMBER', String(10))
    parent_grp = Column('PARENT_GRP', String(10))
    quantity = Column('QTY', Numeric(scale=12, precision=2))
    registration_number = Column('REGISTRATIONNUMBER', String(10))
    sales_description = Column('SALESDESCR', String(80))
    section_profile_rim = Column('SectionProfileRim', String(150))
    stock_code = Column('STKCODE', String(16))
    stock_description = Column('STKDESCR', String(30))
    summary_code = Column('SUMCODE', String(1))
    status = Column('WIPStatusDesc', String(50))
    tyre_requirements = Column('TyreRequirements', String(8000))
    vehicle_mileage = Column('VehicleMileage', Integer)
    vehicle_trailer_make = Column('VehicleTrailerMake', String(8000))


class Supplier(Base):
    __table_args__ = {'schema': 'CamShared'}
    __tablename__ = 'Supplier'

    id = Column('SupplierId', Integer, primary_key=True)
    supplier_code = Column('SupplierCode', String(30))


class SupplierNetwork(Base):
    __table_args__ = {'schema': 'CamShared'}
    __tablename__ = 'SupplierNetwork'

    id = Column('SupplierNetworkId', Integer, primary_key=True)
    supplier_id = Column(Integer, ForeignKey(Supplier.id))
    network_id = Column(Integer, ForeignKey(Network.id))
    supplier_network_code = Column(String(15))
