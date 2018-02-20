import uuid
import datetime

class show():
    def __init__(self,name,date,time,web,wid,sections=None):
        self.wid = wid                                                  # show ID
        self.name = name                                                # show name
        self.web = web                                                  # show website
        self.date = date                                                # show date
        self.time = time                                                # show time
        self.sections = []                                              # show sections
        self.tickets = []                                               # show tickets (tid)
        self.donations = []                                             # tickets donated to show
        self.donations_wait = []                                        # requests for donation
        
class section():
    def __init__(self,price,sid,name):
        self.sid=sid                                                    # sections number
        self.seating = []                                               # seats in section
        self.price = price                                              # section ticket cost
        self.name = name                                                # section name

class seat():
    def __init__(self,row,snum,cid,sid):
        self.cid = cid                                                  # chair id
        self.snum = snum                                                # actual seat number
        self.row = row                                                  # row where seat is
        self.sid = sid                                                  # section where seat is
        self.status = "available"                                       # changes to 'sold' when...sold

class ticket():
    def __init__(self,price,wid,cid,oid):
        self.tid=uuid.uuid4()                                           # unique ID number
        self.price = price                                              # price based on section
        self.status = "Open"                                            # unused ticket, changes to 'used' or 'donated'
        self.wid = wid                                                  # show id
        self.cid = cid                                                  # chair id
        self.oid = oid                                                  # order id

class order():
    def __init__(self,count,pid,wid,total,did=None,status='assigned'):
        self.oid=uuid.uuid4()                                           # unique ID number
        self.count = count                                              # total tickets on order
        self.pid=pid                                                    # patron id number
        self.tickets = []                                               # tid of tickets on order
        self.did = did                                                  # if donated, donated id
        self.wid = wid                                                  # show id for ticket
        self.status = status                                            # status-assigned or pending when waiting for donation
        self.time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")  # creation time
        self.total = total                                              # total cost

class patron():
    def __init__(self,name,phone,email,address,cc,cc2):
        self.pid=uuid.uuid4()                                           # unique ID number
        self.name = name                                                # customer name
        self.phone = phone                                              # customer phone
        self.email = email                                              # customer email
        self.billing_address = address                                  # customer address
        self.cc_number = cc                                             # credit card number
        self.cc_expiration_date = cc2                                   # credit card expiration date
        self.orders = []                                                # orders placed by customer

class reports():
    def __init__(self,mrid,name):
        self.mrid = mrid                                                # report id number
        self.name = name                                                # report name/description

class theater():
    def __init__(self,sections):
        self.sections = sections                                        # all sections in theater (from template creation)
        self.shows = []                                                 # all shows for theater
        self.tix = []                                                   # list of tickets
        self.orders = []                                                # list of orders
        self.patrons = []                                               # list of patrons
        self.reports = None                                             # this is generated with theater creation
