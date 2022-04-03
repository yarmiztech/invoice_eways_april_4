from odoo import models, fields, api
from datetime import datetime, date
from uuid import uuid4

from odoo import api, fields, models, _

from datetime import date
from datetime import datetime
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
import calendar
import re
import json
from dateutil.relativedelta import relativedelta
import pgeocode
import qrcode
from PIL import Image
from random import choice
from string import digits


import math
import re
from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = "account.move"

    sub_supply_type = fields.Selection([('supply', 'Supply'), ('export', 'Export'), ('job', 'Job Work')], copy=False,
                                       string="Sub Supply Type", default='supply')



    def extended_eway(self):
        import requests

        # url = "https://gsp.adaequare.com/test/enriched/ewb/ewayapi"
        # url = "https://gsp.adaequare.com/test/enriched/ewb/ewayapi"
        url_ref = self.env['eway.configuration'].search([('company_id','=',self.company_id.id),('active', '=', True)])
        if url_ref:
            url = url_ref.eway_url
        access_token = self.env['eway.configuration'].search([('company_id','=',self.company_id.id),('active', '=', True)]).access_token

        querystring = {"action": "EXTENDVALIDITY"}
        self.request_id +=1
        barcode_id = self.id
        barcode_search = False
        while not barcode_search:
            ean = str(barcode_id)
            if self.env['account.move'].search([('request_char', '=', ean)]):
                barcode_search = False
                barcode_id += 1
                self.request_char = ean + str(self.invoice_date)
            else:
                barcode_search = True
                if self.request_char:
                    self.request_char = self.request_char+ean + str(self.invoice_date)
                else:
                   self.request_char = ean + str(self.invoice_date)
        # self.request_char = ean
        # self.request_char = 'Extended'+str(self.request_id)

        payload = {"addressLine3": "",
                   "addressLine2": "",
                   "addressLine1": "",
                   "extnRemarks": "Transhipment",
                   "extnRsnCode": 4,
                   "remainingDistance": 0,
                   "consignmentStatus": "M",
                   "isInTransit": "",
                   # "ewbNo": 331002720204,
                   # "ewbNo": 371002721676,
                   "ewbNo": int(self.eway_bill_no),
                   # "vehicleNo": "KA05AK4749",
                   "vehicleNo": self.vehicle_number,
                   # "fromPlace": "Tal. Anjar Dist. Kutch",
                   "fromPlace": self.from_area.name,
                   # "fromStateCode": 29,
                   "fromStateCode": int(self.company_id.state_id.l10n_in_tin),
                   # "fromState": 29,
                   "fromState": int(self.company_id.state_id.l10n_in_tin),
                   # "frompincode": 560063,
                   "frompincode": int(self.company_id.zip) or int(self.from_pin),
                   "Transmode": "1",
                   # "Transdocno": "KA1243",
                   "Transdocno": self.transporter_doc_no or None,
                   "Transdocdate": ""}
        payload = json.dumps(payload)
        print(payload)
        headers = {
            # 'gstin': "05AAACG2115R1ZN",
            'gstin':self.company_id.vat,
            'content-type': "application/json",
            'username': url_ref.sand_user_name,
            # 'requestid': "GK12345672Q1R1125422132d141",
            'requestid': self.request_char,
            'password': url_ref.sand_user_name,
            # 'authorization': "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzY29wZSI6WyJnc3AiXSwiZXhwIjoxNjMzMTYwNTM2LCJhdXRob3JpdGllcyI6WyJST0xFX1NCX0VfQVBJX0VJIiwiUk9MRV9TQl9FX0FQSV9FV0IiXSwianRpIjoiYjFkODE1OTctZTlkYi00MmZjLTk1OTItZTNkYjI2ZWFiOWE4IiwiY2xpZW50X2lkIjoiNDk3QjY3RUM3NDcxNDZDRjk3N0I1MDRFRkFDMTBGMjMifQ.5QEdOemrPadgKGgxyXHJOAKSNQiScNGAYLvDrH6KX7M",
            'authorization': 'Bearer' + ' ' + access_token,
            'cache-control': "no-cache",
            'postman-token': "c6da8124-b7f0-5738-7ee0-b47689cf9515"
        }

        response = requests.request("POST", url, data=payload, headers=headers, params=querystring)

        print(response.text)

        if response.text.split('success":', 1)[1].rsplit(',')[0] == 'true':
            print(response.text)
            url_ref.no_of_calls += 1
            self.extended_eway_date = datetime.now()
            t = datetime.now() + relativedelta(day=datetime.now().day + 1)
            self.extended_eway_update = t + relativedelta(minutes=20)
            # message = response.text.split('message":', 1)[1].rsplit(',')[0]
            # raise UserError(message)
        else:
            print('dfdgd')
            message = response.text.split('message":', 1)[1].rsplit(',')[0]
            raise UserError(message)

        # import requests
        #
        # url = "https://gsp.adaequare.com/test/enriched/ewb/ewayapi"
        #
        # querystring = {"action": "EXTENDVALIDITY"}
        #
        # payload = {"addressLine3": self.partner_id.city,
        #            "addressLine2": self.partner_id.street2,
        #            "addressLine1": self.partner_id.street,
        #            "extnRemarks": "Others",
        #            "extnRsnCode": 99,
        #            "remainingDistance": 10,
        #            # "consignmentStatus": "M",
        #            "isInTransit": "",
        #            "ewbNo": int(self.eway_bill_no),
        #            "vehicleNo": self.vehicle_number,
        #            "fromPlace": self.company_id.city,
        #            "fromStateCode": int(self.company_id.state_id.l10n_in_tin),
        #            "fromState": int(self.company_id.state_id.l10n_in_tin),
        #            "frompincode": self.company_id.zip,
        #            "transMode": "5",
        #            "consignmentStatus": "T",
        #            "transitType": "R",
        #            "Transdocno": self.transporter_doc_no,
        #            "Transdocdate": re.sub(r'(\d{4})-(\d{1,2})-(\d{1,2})', '\\3-\\2-\\1',
        #                                   str(self.document_date)).replace(
        #                '-', '/'), }
        #
        # # payload = "{\n\"addressLine3\": \"\",\n\"addressLine2\": \"\",\n\"addressLine1\": \"\",\n\"extnRemarks\": \"Others\",\n\"extnRsnCode\": 99,\n\"remainingDistance\": 10,\n\"consignmentStatus\": \"M\",\n\"isInTransit\":\"\",\n\"ewbNo\": 371002718834,\n\"vehicleNo\": \"KA05AK4749\",\n\"fromPlace\": \"Tal. Anjar Dist. Kutch\",\n\"fromStateCode\":29,\n\"fromState\": 29,\n\"frompincode\": 560063,\n\"Transmode\": \"1\",\n\"Transdocno\": \"KA1243\",\n\"Transdocdate\": \"\"\n}"
        # payload = json.dumps(payload)
        # print(payload)
        #
        # headers = {
        #     'gstin': "05AAACG2115R1ZN",
        #     'content-type': "application/json",
        #     'username': "05AAACG2115R1ZN",
        #     'requestid': "GK123456QR1144456df223882",
        #     'password': "abc123@@",
        #     'authorization': "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzY29wZSI6WyJnc3AiXSwiZXhwIjoxNjMzMTYwNTM2LCJhdXRob3JpdGllcyI6WyJST0xFX1NCX0VfQVBJX0VJIiwiUk9MRV9TQl9FX0FQSV9FV0IiXSwianRpIjoiYjFkODE1OTctZTlkYi00MmZjLTk1OTItZTNkYjI2ZWFiOWE4IiwiY2xpZW50X2lkIjoiNDk3QjY3RUM3NDcxNDZDRjk3N0I1MDRFRkFDMTBGMjMifQ.5QEdOemrPadgKGgxyXHJOAKSNQiScNGAYLvDrH6KX7M",
        #     'cache-control': "no-cache",
        #     'postman-token': "f7c80233-908a-1684-0138-195b684ca925"
        # }
        #
        # response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
        #
        # print(response.text)
    def generate_eway_by_irn(self):

        import requests

        # url = "https://gsp.adaequare.com/test/enriched/ei/api/ewaybill"

        url_ref = self.env['eway.configuration'].search([('company_id','=',self.company_id.id),('active', '=', True)])
        if url_ref:
            url = url_ref.eway_by_irn
            username = url_ref.sand_user_name
            password = url_ref.sand_password
            access_token = url_ref.access_token
        self.request_id +=1
        barcode_id = self.id
        barcode_search = False
        while not barcode_search:
            ean = str(barcode_id)
            if self.env['account.move'].search([('request_char', '=', ean)]):
                barcode_search = False
                barcode_id += 1
                self.request_char = ean + str(self.invoice_date)
            else:
                barcode_search = True
                if self.request_char:
                    self.request_char = self.request_char + str(self.invoice_date)
                else:
                    self.request_char = ean + str(self.invoice_date)
        # self.request_char = ean
        # self.request_char = "BYIRNEWAY"+str(self.request_id)
        # access_token = self.env['eway.configuration'].search([('active', '=', True)]).access_token
        doc_date =None
        if self.document_date:
            doc_date = re.sub(r'(\d{4})-(\d{1,2})-(\d{1,2})', '\\3-\\2-\\1', str(self.document_date)).replace(
                '-', '/')
        transportation_date = None
        if self.transportation_date:
            transportation_date =  re.sub(r'(\d{4})-(\d{1,2})-(\d{1,2})', '\\3-\\2-\\1',
                   str(self.transportation_date)).replace(
                '-', '/')

        payload = {"Irn": self.irn,
                   "Distance": 0,
                   "TransMode": "1",
                   # "TransId": '04AMBPG7773M002',
                   "TransId": self.transporter.transporter_id or None,
                   # "TransId": '',
                   "TransName": self.transporter.name or None,
                   # "TransDocDt": re.sub(r'(\d{4})-(\d{1,2})-(\d{1,2})', '\\3-\\2-\\1',
                   #                      str(self.transportation_date)).replace(
                   #     '-', '/'),
                   "TransDocDt": transportation_date,
                   "TransDocNo": self.transporter_doc_no or None,
                   # "TransDocNo": self.name,
                   "VehNo": self.vehicle_number,
                   "VehType": "R"
                   }
        payload = json.dumps(payload)
        headers = {
            'content-type': "application/json",
            # 'user_name': "adqgspjkusr1",
            'user_name': url_ref.user_name,
            # 'password': "Gsp@1234",
            'password': url_ref.ewb_password,
            # 'gstin': "01AMBPG7773M002",
            'gstin': url_ref.gstin,
            # 'requestid': "dyd1433d1i1631k2k112x11cdd1fw3dw4334354",
            'requestid':self.request_char,
            # 'authorization': "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzY29wZSI6WyJnc3AiXSwiZXhwIjoxNjMzMTYwNTM2LCJhdXRob3JpdGllcyI6WyJST0xFX1NCX0VfQVBJX0VJIiwiUk9MRV9TQl9FX0FQSV9FV0IiXSwianRpIjoiYjFkODE1OTctZTlkYi00MmZjLTk1OTItZTNkYjI2ZWFiOWE4IiwiY2xpZW50X2lkIjoiNDk3QjY3RUM3NDcxNDZDRjk3N0I1MDRFRkFDMTBGMjMifQ.5QEdOemrPadgKGgxyXHJOAKSNQiScNGAYLvDrH6KX7M",
            'authorization': 'Bearer' + ' ' + access_token,
            'cache-control': "no-cache",
            'postman-token': "b7d9ca05-73d0-eb00-9952-02af90ae2815"
        }

        response = requests.request("POST", url, data=payload, headers=headers)

        print(response.text)
        if response.text.split('success":', 1)[1].rsplit(',')[0] == 'true':
            url_ref.no_of_calls += 1
            self.eway_bill_no = response.text.split('result":', 1)[1].split('EwbNo":', 1)[1].rsplit(',')[0]
            self.eway_bill_date = datetime.now()
            self.eway_valid_up = datetime.now() + relativedelta(day=datetime.now().day + 1)
        else:
            print('dfdgd')
            message = response.text.split('message":', 1)[1].rsplit(',')[0]
            raise UserError(message)
    def action_create_irn(self):
        list = []
        val_list = []
        val_m = {}
        i = 0
        doc_date = None
        if self.document_date:
            doc_date = re.sub(r'(\d{4})-(\d{1,2})-(\d{1,2})', '\\3-\\2-\\1', str(self.document_date)).replace(
                '-', '/')
        for line in self.invoice_line_ids:
            if line.product_id:
                i = i + 1
                tax = 0
                if line.tax_ids:
                    tax = 0
                    for each in line.tax_ids:
                        if each.children_tax_ids:
                            for ch in each.children_tax_ids:
                                tax = ch.amount
                        else:
                            tax = each.amount

                print(tax, 'tax')
                cgst = 0
                igst = 0
                if len(line.tax_ids.children_tax_ids) == 2:
                    cgst = self.amount_tax / len(line.tax_ids.children_tax_ids)
                if len(line.tax_ids.children_tax_ids) == 0:
                    igst = self.amount_tax

                mou = {
                    "SlNo": str(i),
                    # "PrdDesc": line.product_id.name,
                    "PrdDesc": line.product_id.categ_id.name,
                    "IsServc": "N",
                    "HsnCd": line.product_id.l10n_in_hsn_code,
                    "Barcde": "123456",
                    "Qty": line.quantity,
                    "FreeQty": 0,
                    "Unit": "BAG",
                    # "Unit": "UNT",
                    "UnitPrice": line.price_unit,
                    "TotAmt": line.price_subtotal,
                    "Discount": 0,
                    "PreTaxVal": 0,
                    "AssAmt": line.price_subtotal - 0,
                    # "AssAmt":  0,
                    # "GstRt": 0,
                    "GstRt": int(line.tax_ids.amount),
                    # "GstRt": 0,
                    # "IgstAmt": self.amount_tax,
                    "IgstAmt": igst,
                    # "IgstAmt": 0,
                    # "CgstAmt": self.amount_tax,
                    # "CgstAmt": 0,
                    "CgstAmt": cgst,
                    "SgstAmt": cgst,
                    # "SgstAmt": self.amount_tax/2,
                    "CesRt": 0,
                    "CesAmt": 0,
                    "CesNonAdvlAmt": 0,
                    "StateCesRt": 0,
                    "StateCesAmt": 0,
                    # "StateCesAmt": self.amount_tax,
                    "StateCesNonAdvlAmt": 0,
                    "OthChrg": 0,
                    # "TotItemVal": line.price_subtotal,
                    "TotItemVal": self.amount_total,
                    "OrdLineRef": "3256",
                    "OrgCntry": "AG",
                    "PrdSlNo": "12345",
                    "BchDtls": {"Nm": "123456",
                                "Expdt": doc_date,
                                "wrDt": doc_date},
                    "AttribDtls": [{"Nm": line.product_id.categ_id.name,
                                    "Val": str(line.price_subtotal)}]
                }
                list.append(mou)
                val_m = {
                    "AssVal": line.price_subtotal - 0,
                    "CgstVal": cgst,
                    "SgstVal": cgst,
                    # "IgstVal":0,
                    # "IgstVal": self.amount_tax,
                    "IgstVal": igst,
                    "CesVal": 0,
                    "StCesVal": 0,
                    "Discount": 0,
                    "OthChrg": 0,
                    "RndOffAmt": 0.0,
                    # "TotInvVal": line.price_subtotal,
                    "TotInvVal": self.amount_total,
                    # "TotInvValFc": line.price_subtotal
                    "TotInvValFc": self.amount_total
                }
                val_list.append(val_m)

        direct = {}
        if self.state == 'paid':
            direct = {
                "Nm": self.partner_id.name,
                # "Accdet": "5697389713210",
                "Accdet": self.partner_id.bank_ids.acc_number,
                "Mode": "Cash",
                "Fininsbr": self.partner_id.bank_ids.bank_id.name,
                # "Fininsbr": "SBIN11000",
                "Payterm": "100",
                "Payinstr": "Gift",
                "Crtrn": "test",
                "Dirdr": "test",
                "Crday": 100,
                "Paidamt": self.amount_total,
                "Paymtdue": self.residual
            }

        import requests

        # url = "https://gsp.adaequare.com/test/enriched/ei/api/invoice"
        # url_ref = self.env['eway.configuration'].search([('active', '=', True)])
        url_ref = self.env['eway.configuration'].search([('company_id','=',self.company_id.id),('active', '=', True)])
        username = ''
        password = ''
        access_token = ''
        if url_ref:
            url = url_ref.irn_einvoice
            username = url_ref.sand_user_name
            password = url_ref.sand_password
            access_token = url_ref.access_token
        self.request_id += 1
        barcode_id = self.id
        barcode_search = False
        while not barcode_search:
            # ean = generate_ean(str(barcode_id))
            ean = str(barcode_id)
            if self.env['account.move'].search([('request_char', '=', ean)]):
                barcode_search = False
                barcode_id += 1
                self.request_char = ean +str(self.request_id)+ str(self.invoice_date)
            else:
                barcode_search = True
                if self.request_char:
                    self.request_char = self.request_char+self.uuid
                else:
                   self.request_char = ean + str(self.request_id)+str(self.invoice_date) + self.uuid

        transportation_date = None
        if self.transportation_date:
            transportation_date =  re.sub(r'(\d{4})-(\d{1,2})-(\d{1,2})', '\\3-\\2-\\1',
                   str(self.transportation_date)).replace(
                '-', '/')

        payload = {
            "Version": "1.1",
            "TranDtls": {
                "TaxSch": "GST",
                "SupTyp": "B2B",
                "RegRev": "N",
                "EcmGstin": None,
                "IgstOnIntra": "N"
            },
            "DocDtls": {
                "Typ": "INV",
                # "No": self.transporter_doc_no or None,
                "No": self.name,
                # "Dt": re.sub(r'(\d{4})-(\d{1,2})-(\d{1,2})', '\\3-\\2-\\1',
                #              str(self.document_date)).replace('-', '/')
                "Dt":doc_date
            },
            "SellerDtls": {
                # "Gstin": "01AMBPG7773M002",
                "Gstin": self.company_id.vat,
                "LglNm": self.company_id.name,
                "TrdNm": self.company_id.name,
                "Addr1": self.company_id.street or self.from_area.name,
                # "Addr1": "5th block, kuvempu layout",
                "Addr2": self.company_id.street2 or self.from_area.name,
                # "Loc": "GANDHINAGAR",
                "Loc": self.company_id.city or self.from_area.name,
                # "Pin": 193502,
                "Pin": int(self.company_id.zip) or int(self.from_pin),
                "Stcd": self.company_id.state_id.l10n_in_tin,
                # "Stcd": "36",
                # "Stcd": self.partner_id.state_id.code,
                # "Ph": "9000000000",
                "Ph": self.company_id.phone or None,
                # "Em": "abc@gmail.com"
                "Em": self.company_id.email or None
            },
            "BuyerDtls": {
                # "Gstin": "36AMBPG7773M002",
                "Gstin": self.partner_id.vat,
                "LglNm": self.partner_id.name,
                "TrdNm":self.partner_id.name,
                # "Pos": "12",
                "Pos": self.partner_id.state_id.l10n_in_tin,
                # "Pos": "",
                # "Addr1": "7th block, kuvempu layout",
                "Addr1": self.partner_id.street or self.to_area.name,
                "Addr2": self.partner_id.street2 or self.to_area.name,
                # "Loc": "GANDHINAGAR",
                "Loc": self.partner_id.city or self.to_area.name,
                "Pin": int(self.partner_id.zip) or int(self.to_pin),
                # "Stcd": "36",
                # "Pin": 500055,
                # "Stcd": self.partner_id.state_id.code,
                "Stcd": self.partner_id.state_id.l10n_in_tin,
                # "Ph": "91111111111",
                "Ph": self.partner_id.mobile or None,
                "Em": self.partner_id.email  or None
            },
            # "DispDtls": {
            #     # "Nm": "ABC company pvt ltd",
            #     "Nm": self.partner_id.name,
            #     # "Addr1": "7th block, kuvempu layout",
            #     "Addr1": self.partner_id.street,
            #     # "Addr2": "kuvempu layout",
            #     "Addr2": self.partner_id.street2,
            #     # "Loc": "Banagalore",
            #     "Loc": self.partner_id.city,
            #     # "Pin": 562160,
            #     "Pin": int(self.partner_id.zip),
            #     # "Stcd": "36",
            #     # "Stcd": self.partner_id.state_id.code
            #     "Stcd": self.partner_id.state_id.l10n_in_tin
            # },
            # "ShipDtls": {
            #     # "Gstin": "36AMBPG7773M002",
            #     "Gstin": self.partner_id.vat,
            #     # "LglNm": "CBE company pvt ltd",
            #     "LglNm": self.partner_id.name,
            #     # "TrdNm": "kuvempu layout",
            #     "TrdNm": self.partner_id.name,
            #     # "Addr1": "7th block, kuvempu layout",
            #     "Addr1": self.partner_id.street,
            #     # "Addr2": "kuvempu layout",
            #     "Addr2": self.partner_id.street2,
            #     # "Loc": "Banagalore",
            #     "Loc": self.partner_id.city,
            #     # "Pin": 500055,
            #     "Pin": int(self.partner_id.zip),
            #     # "Stcd": "36",
            #     "Stcd": self.partner_id.state_id.l10n_in_tin
            # },
            "ItemList": list,
            "ValDtls": val_m,
            "PayDtls": direct,
            "RefDtls": {
                "InvRm": "TEST",
                "DocPerdDtls": {
                    # "InvStDt": "01/08/2020",
                    # "InvStDt":self.date_invoice,
                    "InvStDt": re.sub(r'(\d{4})-(\d{1,2})-(\d{1,2})', '\\3-\\2-\\1', str(self.invoice_date)).replace(
                        '-', '/'),
                    # "InvEndDt": "01/09/2020"
                    "InvEndDt": re.sub(r'(\d{4})-(\d{1,2})-(\d{1,2})', '\\3-\\2-\\1', str(self.invoice_date_due)).replace(
                        '-', '/'),
                },
                "PrecDocDtls": [
                    {
                        # "InvNo": "20S51s90562344",
                        # "InvNo": self.transporter_doc_no,
                        "InvNo":self.name,
                        # "InvNo": self.name,
                        # "InvDt": "01/08/2020",
                        "InvDt": re.sub(r'(\d{4})-(\d{1,2})-(\d{1,2})', '\\3-\\2-\\1', str(self.invoice_date)).replace(
                            '-', '/'),
                        "OthRefNo": "inv ref"
                        # "OthRefNo": self.origin
                    }
                ],
                # "ContrDtls": [
                #     {
                #         "RecAdvRefr": "Doc/003",
                #         "RecAdvDt": re.sub(r'(\d{4})-(\d{1,2})-(\d{1,2})', '\\3-\\2-\\1', str(self.invoice_date)).replace(
                #             '-', '/'),
                #         "Tendrefr": "Abc001",
                #         "Contrrefr": "Co123",
                #         "Extrefr": "Yo456",
                #         "Projrefr": "Doc-456",
                #         "Porefr": "Doc-789",
                #         # "PoRefDt": re.sub(r'(\d{4})-(\d{1,2})-(\d{1,2})', '\\3-\\2-\\1',
                #         #                     str(self.document_date)).replace('-', '/')
                #         "PoRefDt": doc_date
                #     }
                # ]
            },
            # "AddlDocDtls": [
            #     {
            #         "Url": "https://einv-apisandbox.nic.in",
            #         "Docs": "Test Doc",
            #         "Info": "Document Test"
            #     }
            # ],
            # "ExpDtls": {
            #     # "ShipBNo": self.transporter_doc_no,
            #     "ShipBNo": self.name,
            #     # "ShipBDt": re.sub(r'(\d{4})-(\d{1,2})-(\d{1,2})', '\\3-\\2-\\1',
            #     #              str(self.document_date)).replace('-', '/'),
            #     "ShipBDt": doc_date,
            # }
        }
        payload = json.dumps(payload)
        print(payload)
        headers = {
            'content-type': "application/json",
            # 'user_name': "adqgspjkusr1",
            'user_name': url_ref.user_name,
            # 'password': "Gsp@1234",
            'password': url_ref.ewb_password,
            # 'gstin': "01AMBPG7773M002",
            'gstin': url_ref.gstin,
            # 'requestid': "IrE4pet12u63iuyz124144e5e58114dd33272",
            'requestid': self.request_char,
            # 'authorization': "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzY29wZSI6WyJnc3AiXSwiZXhwIjoxNjMzMTYwNTM2LCJhdXRob3JpdGllcyI6WyJST0xFX1NCX0VfQVBJX0VJIiwiUk9MRV9TQl9FX0FQSV9FV0IiXSwianRpIjoiYjFkODE1OTctZTlkYi00MmZjLTk1OTItZTNkYjI2ZWFiOWE4IiwiY2xpZW50X2lkIjoiNDk3QjY3RUM3NDcxNDZDRjk3N0I1MDRFRkFDMTBGMjMifQ.5QEdOemrPadgKGgxyXHJOAKSNQiScNGAYLvDrH6KX7M",
            'authorization': 'Bearer' + url_ref.access_token,
            'cache-control': "no-cache",
            'postman-token': "bb2ef593-7b1b-4091-0433-e518d2b55ee9"
        }

        response = requests.request("POST", url, data=payload, headers=headers)
        print(response.text)
        if response.text.split('success":', 1)[1].rsplit(',')[0] == 'true':
            print(response.text)
            self.irn = response.text.split('result":', 1)[1].split('Irn":', 1)[1].rsplit(',')[0].split('"')[1]
            self.irn_ack_dt = datetime.now()
            self.irn_ack_no = response.text.split('AckNo', 1)[1].rsplit('":')[1].rsplit(',')[0]
            self.signed_inv = response.text.split('result":', 1)[1].split('SignedInvoice', 1)[1].rsplit(':')[1].rsplit('"')[1]
            self.signed_qr_inv = response.text.split('result":', 1)[1].split('SignedInvoice', 1)[1].rsplit(':')[2].rsplit('"')[1]
            url_ref.no_of_calls += 1
            self.no_of_calls += 1
            # message = response.text.split('message":', 1)[1].rsplit(',')[0]
            # raise UserError(message)
        else:
            print('dfdgd')
            message = response.text.split('message":', 1)[1].rsplit(',')[0]
            raise UserError(message)
    def action_e_way_confirm(self):
        if self.eway_bill_no:
            raise UserError(
                _('You can not create E-way bill Again for this Invoice.'))

        import requests

        # url = "https://gsp.adaequare.com/test/enriched/ewb/ewayapi"
        url_ref = self.env['eway.configuration'].search([('company_id','=',self.company_id.id),('active', '=', True)])
        if url_ref:
            url = url_ref.eway_url

        querystring = {"action": "GENEWAYBILL"}

        from dateutil.relativedelta import relativedelta
        import re
        line_list = []
        for line in self.invoice_line_ids:
            if line.product_id:
                tax = 0
                if line.tax_ids:
                    tax = 0
                    for each in line.tax_ids:
                        if each.children_tax_ids:
                            for ch in each.children_tax_ids:
                                tax = ch.amount
                        else:
                            tax = each.amount

                print(tax, 'tax')
                cgst = 0
                igst = 0
                cgst_tax = 0
                igst_tax = 0
                if len(line.tax_ids.children_tax_ids) == 2:
                    # cgst = self.amount_tax / len(line.invoice_line_tax_ids.children_tax_ids)
                    cgst = tax
                    cgst_tax = self.amount_tax/2
                if len(line.tax_ids.children_tax_ids) == 0:
                    igst = tax
                    igst_tax = self.amount_tax
                    # igst = self.amount_tax

                products_list = {'productName': line.product_id.categ_id.name,
                                 'productDesc': line.product_id.categ_id.name,
                                 # 'hsnCode': 1001,
                                 'hsnCode': int(line.product_id.l10n_in_hsn_code),
                                 'quantity': line.quantity,
                                 'qtyUnit': 'BAG',
                                 # 'qtyUnit': 'UNT',
                                 'cgstRate': cgst,
                                 'sgstRate': cgst,
                                 'igstRate': igst,
                                 'cessRate': 0,
                                 'cessAdvol': 0,
                                 'taxableAmount': self.amount_untaxed}
                line_list.append(products_list)
            # print(line_list)
        doc_date =None
        if self.document_date:
            doc_date = re.sub(r'(\d{4})-(\d{1,2})-(\d{1,2})', '\\3-\\2-\\1', str(self.document_date)).replace(
                '-', '/')
        transportation_date = None
        if self.transportation_date:
            transportation_date =  re.sub(r'(\d{4})-(\d{1,2})-(\d{1,2})', '\\3-\\2-\\1',
                   str(self.transportation_date)).replace(
                '-', '/')

        payload = {'supplyType': 'O',
                   'subSupplyType': '1',
                   'docType': 'INV',
                   # 'docNo': self.transporter_doc_no or None,
                   'docNo': self.name or None,
                   # 'docDate': str(self.document_date),
                   # 'docDate': re.sub(r'(\d{4})-(\d{1,2})-(\d{1,2})', '\\3-\\2-\\1', str(self.document_date)).replace(
                   #     '-', '/'),
                   'docDate':doc_date,
                   # 'fromGstin': '05AAACG2115R1ZN',
                   'fromGstin': self.company_id.vat,
                   'fromTrdName': self.company_id.name,
                   'fromAddr1': self.company_id.street,
                   'fromAddr2': self.company_id.street2,
                   'fromPlace': self.company_id.city,
                   'fromPincode': int(self.company_id.zip) or int(self.from_pin),
                   # 'fromPincode': 560042,
                   'actFromStateCode': int(self.company_id.state_id.l10n_in_tin),
                   # 'actFromStateCode': 29,
                   'fromStateCode': int(self.company_id.state_id.l10n_in_tin),
                   # 'fromStateCode': 29,
                   'toGstin': self.partner_id.vat,
                   'toTrdName': self.partner_id.name,
                   'toAddr1': self.partner_id.street or self.to_area.name,
                   'toAddr2': self.partner_id.street2 or self.to_area.name,
                   'toPlace': self.to_area.name or self.partner_id.city,
                   'toPincode': int(self.partner_id.zip) or int(self.to_pin),
                   'actToStateCode': int(self.partner_id.state_id.l10n_in_tin),
                   'toStateCode': int(self.partner_id.state_id.l10n_in_tin),
                   'totalValue': self.amount_untaxed,
                   # 'cgstValue': 0,
                   # 'cgstValue': cgst,
                   'cgstValue': cgst_tax,
                   # 'sgstValue': 0,
                   'sgstValue': cgst_tax,
                   # 'igstValue': self.amount_tax / 2,
                   'igstValue': igst_tax,
                   'cessValue': 0,
                   'totInvValue': self.amount_total,
                   'transporterId': self.transporter.transporter_id or None,
                   'transporterName': self.transporter.name or None,
                   # 'transDocNo': '',
                   'transDocNo': self.transporter_doc_no or None,
                   'transMode': '1',
                   'transDistance': str(self.distance),
                   # 'transDocDate': re.sub(r'(\d{4})-(\d{1,2})-(\d{1,2})', '\\3-\\2-\\1',
                   #                        str(self.transportation_date)).replace(
                   #     '-', '/'),
                   'transDocDate':transportation_date,
                   'vehicleNo': self.vehicle_number,
                   'vehicleType': 'R',
                   'TransactionType': '1',
                   # 'itemList': [
                   #     {'productName': self.invoice_line_ids.product_id.name,
                   #      'productDesc': self.invoice_line_ids.product_id.name,
                   #      'hsnCode': int(line.product_id.l10n_in_hsn_code),
                   #      'quantity': self.invoice_line_ids.quantity,
                   #      'qtyUnit': 'UNT',
                   #      'cgstRate': cgst,
                   #      'sgstRate': cgst,
                   #      'igstRate': igst,
                   #      'cessRate': 0,
                   #      'cessAdvol': 0,
                   #      'taxableAmount': self.amount_untaxed}]}
        'itemList':line_list}

        # }

        # payload = "{\n   'supplyType': 'O',\n  'subSupplyType': '1',\n   'docType': 'INV',\n   'docNo': '123m7lh5125',\n    'docDate': '15/12/2017',\n    'fromGstin': '05AAACG2115R1ZN',\n 'fromTrdName': 'welton',\n    'fromAddr1': '2ND CROSS NO 59  19  A',\n    'fromAddr2': 'GROUND FLOOR OSBORNE ROAD',\n   'fromPlace': 'FRAZER TOWN',\n  'fromPincode': 560042,\n  'actFromStateCode': 29,\n   'fromStateCode': 29,\n  'toGstin': '05AAACG2140A1ZL',\n   'toTrdName': 'sthuthya',\n 'toAddr1':'Shree Nilaya',\n 'toAddr2': 'Dasarahosahalli',\n    'toPlace': 'Beml Nagar',\n    'toPincode': 500003,\n  'actToStateCode': 36,\n  'toStateCode': 36,\n  'totalValue': 5609889,\n   'cgstValue': 0,\n  'sgstValue': 0,\n 'igstValue': 168296.67,\n   'cessValue': 224395.56,\n 'totInvValue': 6002581.23,\n 'transporterId': '\',\n    'transporterName': '\','transDocNo':'\',\n  'transMode': '1',\n    transDistance': '25',\n   'transDocDate': '\',\n    'vehicleNo': 'PVC1234',\n   'vehicleType': 'R',\n  'TransactionType':'1',\n   'itemList': [{\n  'productName':'Wheat',\n   'productDesc': 'Wheat',\n   'hsnCode': 1001,\n    'quantity\': 4,\n        'qtyUnit': 'BOX',\n        'cgstRate': 0,\n     'sgstRate': 0,\n     'igstRate': 3,\n    'cessRate': 1,\n    'cessAdvol': 0,\n 'taxableAmount': 5609889\n    } }]\n}"
        m = []
        import json
        payload = json.dumps(payload)
        print(payload)
        # access_token = self.env['eway.configuration'].search([]).access_token
        url_ref = self.env['eway.configuration'].search([('company_id','=',self.company_id.id),('active', '=', True)])
        username = ''
        password = ''
        access_token = ''
        if url_ref:
            username = url_ref.sand_user_name
            password = url_ref.sand_password
            access_token = url_ref.access_token
            access_gstin = url_ref.gstin
        self.request_id += 1
        barcode_id = self.id
        barcode_search = False
        while not barcode_search:
            ean = str(barcode_id)
            if self.env['account.move'].search([('request_char', '=', ean)]):
                barcode_search = False
                barcode_id += 1
                self.request_char = ean+str(self.invoice_date)+str(barcode_id)

            else:
                barcode_search = True
                if self.request_char:
                    self.request_char = str(self.request_char)+str(self.invoice_date)+str(self.to_pin)
                else:
                     self.request_char = 'ewb'+str(self.invoice_date)+str(self.to_pin)

        # if not self.request_char:
        #      self.request_char = 'EWAYP2S3314415' + str(self.request_id)


        headers = {
            'content-type': "application/json",
            # 'username': "05AAACG2115R1ZN",
            'username': username,
            # 'password': "abc123@@",
            'password': password,
            # 'gstin': "05AAACG2115R1ZN",
            'gstin': url_ref.gstin,
            # 'requestid': self.transporter_doc_no,
            'requestid': self.request_char,
            # 'authorization': "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzY29wZSI6WyJnc3AiXSwiZXhwIjoxNjMzMTYwNTM2LCJhdXRob3JpdGllcyI6WyJST0xFX1NCX0VfQVBJX0VJIiwiUk9MRV9TQl9FX0FQSV9FV0IiXSwianRpIjoiYjFkODE1OTctZTlkYi00MmZjLTk1OTItZTNkYjI2ZWFiOWE4IiwiY2xpZW50X2lkIjoiNDk3QjY3RUM3NDcxNDZDRjk3N0I1MDRFRkFDMTBGMjMifQ.5QEdOemrPadgKGgxyXHJOAKSNQiScNGAYLvDrH6KX7M",
            'authorization': 'Bearer' + ' ' + access_token,
            'cache-control': "no-cache",
            'postman-token': "860c7249-84b2-9703-a254-bb673c97ccf9"
        }

        response = requests.request("POST", url, data=payload, headers=headers, params=querystring)

        print(response.text)
        if  response.text.split('success":', 1)[1].rsplit(',')[0] == 'true':
            self.eway_bill_no = response.text.rsplit('{')[2].rsplit(':')[1].rsplit('"')[0].rsplit(',')[0]
            self.eway_bill = response.text.rsplit('{')[2].rsplit(':')[1].rsplit('"')[0].rsplit(',')[0]
            self.eway_bill_date = datetime.now()
            url_ref.no_of_calls += 1
            self.no_of_calls += 1
            self.eway_valid_up = datetime.now() + relativedelta(day=datetime.now().day + 1)
        else:
            print('dfdgd')
            message = response.text.split('message":', 1)[1].rsplit(',')[0]
            raise UserError(message)
def check_ean(self, eancode):
    """returns True if eancode is a valid ean13 string, or null"""
    if not eancode:
        return True
    if len(eancode) != 13:
        return False
    try:
        int(eancode)
    except:
        return False
    return self.ean_checksum(eancode) == int(eancode[-1])


def ean_checksum(eancode):
    """returns the checksum of an ean string of length 13, returns -1 if
    the string has the wrong length"""
    if len(eancode) != 13:
        return -1
    oddsum = 0
    evensum = 0
    eanvalue = eancode
    reversevalue = eanvalue[::-1]
    finalean = reversevalue[1:]

    for i in range(len(finalean)):
        if i % 2 == 0:
            oddsum += int(finalean[i])
        else:
            evensum += int(finalean[i])
    total = (oddsum * 3) + evensum

    check = int(10 - math.ceil(total % 10.0)) % 10
    return check


def generate_ean(self, ean):
    """Creates and returns a valid ean13 from an invalid one"""
    if not ean:
        return "0000000000000"
    ean = re.sub("[A-Za-z]", "0", ean)
    ean = re.sub("[^0-9]", "", ean)
    ean = ean[:13]
    if len(ean) < 13:
        ean = ean + '0' * (13 - len(ean))
    return ean[:-1] + str(self.ean_checksum(ean))
