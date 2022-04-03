Tally Integration Configuration

For Working Of this Module We Need "report_xml" module

1.Configuration
        1.Go To --> EnzTally --> Configuration --> Tally Account
           Select the Accounts and Give the Corresponding names of the Accounts in tally

        2.Go To --> EnzTally --> Configuration --> Tally Tax
           Select the Tax and Give the Corresponding names of the Tax in Tally

        3.Go To --> EnzTally --> Configuration --> Tally Unit
           Select the UOM and Give the Corresponding names of the UOM in tally

2.Working
        1.Ledger
          This is For Getting Customer and Vendors Which is there in owr system but not in Tally
          --> Give the Location of the Excel Sheet inside "Location" Field\
          --> Click on Check then we will get the list of customer and supplier in the Below table
          --> Take the XML Report By Going to "Print"

        2.Invoice
          This is For Getting the "Posted" Invoices in odoo, between the corresponding date
          --> Give the "Form date" and "To date"
          -->If Branch Wise needed then select the branch
          --> Take the XML Report By Going to "Print"

        2.Bill
          This is For Getting the "Posted" Vendor Bills in odoo, between the corresponding date
          --> Give the "Form date" and "To date"
          -->If Branch Wise needed then select the branch
          --> Take the XML Report By Going to "Print"

Dynamic Values Need To be added in the Report "report_view_1.xml"
Tags and Lines are given below
 1.IRN
   Lines -- 171,613
 2.IRNACKNO
    Lines -- 188,630,1049
 3.IRNQRCODE
    Lines -- 189,631
 4.BASICSHIPVESSELNO
    Lines -- 191,634,1054
 5.EWATBUILLDETAILS
   1.BILLNUMBER
      Lines -- 280,1143
   2.VALIDUPTO
      Lines -- 1155,292
   3.UPDATEDATE
      Lines -- 1156,292
   4.TRANSPORTMODE
      Lines -- 1158,295
   5.VEHICLENUMBER
      Lines -- 1159,296
   6.VEHICLETYPE
      Lines -- 1160,297
   7.DISTANCE
      Lines -- 1170,307

