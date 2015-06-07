#! /usr/bin/env python3

from datetime import datetime as time
from marshmallow import Schema, fields

import config
from models.documents import Document
from models.odie import Order
from odie import ClientError


def serialize(data, schema, many=False):
    res = schema().dump(data, many)
    if res.errors:
        raise ClientError(*res.errors)
    else:
        return res.data


class IdSchema(Schema):
    id = fields.Int()


class DocumentSchema(IdSchema):
    lectures = fields.List(fields.Nested(IdSchema))
    examinants = fields.List(fields.Nested(IdSchema))
    date = fields.Date()
    number_of_pages = fields.Int()
    solution = fields.Str()
    comment = fields.Str()
    document_type = fields.Str()
    available = fields.Method('is_available_for_printing')

    def is_available_for_printing(self, obj):
        return obj.file_id is not None


class ExaminantSchema(IdSchema):
    name = fields.Str()


class OrderLoadSchema(IdSchema):
    name = fields.Str(required=True)
    document_ids = fields.List(fields.Int(), required=True)

    def make_object(self, data):
        return Order(name=data['name'],
                     document_ids=data['document_ids'])


class OrderDumpSchema(OrderLoadSchema):
    documents = fields.List(fields.Nested(DocumentSchema))


class LectureSchema(IdSchema):
    name = fields.Str()
    aliases = fields.List(fields.Str())
    subject = fields.Str()
    comment = fields.Str()


class DepositSchema(IdSchema):
    price = fields.Int()
    name = fields.Str()
    lectures = fields.List(fields.Str())


class PrintJobLoadSchema(Schema):
    coverText = fields.Str(required=True)
    document_ids = fields.List(fields.Int(), required=True)
    depositCount = fields.Int(required=True)
    printer = fields.Str(required=True, validate=lambda s: s in config.FS_CONFIG['PRINTERS'])

