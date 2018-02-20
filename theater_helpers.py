import theater_classes as tc
from datetime import datetime

def verifier(data,sect,params):

    verifier = True

    for i in params:
        if i not in data[sect]:
            verifier = False

    return verifier

def create_patron(data):
    # parse input data into parts, create patron

    name = data['patron_info']['name']
    phone = data['patron_info']['phone']
    email = data['patron_info']['email']
    billing_address = data['patron_info']['billing_address']
    cc_number = data['patron_info']['cc_number']
    cc_expiration_date = data['patron_info']['cc_expiration_date']

    return tc.patron(name,phone,email,billing_address,cc_number,cc_expiration_date)

def get_patron(t,pid):
    # find patron by id number

    for i in t.patrons:
        if str(i.pid) == str(pid):
            return i

def get_show(t,wid):
    # find show by id number

    for i in t.shows:
        if str(i.wid) == str(wid):
            return i

def get_order(t,oid,did=None):
    # find order by id number or donation id number

    if not did:

        for i in t.orders:
            if str(i.oid) == str(oid):
                return i
    else:
        for i in t.orders:
            if str(i.did) == str(did):
                return i

def get_ticket(t,tid):
    # find ticket by id number

    for i in t.orders:
        for j in i.tickets:
            if str(j.tid) == str(tid):
                return j

def get_sect(t,sid,wid=None):
    # find section by id number or show id

    if wid:
        s = get_show(t,wid)
        for i in s.sections:
            if str(sid) == str(i.sid):
                return i
    else:
        for i in t.sections:
            if str(sid) == str(i.sid):
                return i

def dupe_show(t,date,time):
    # check if a show is duplicated

    ret = True

    for i in t.shows:
        if i.date == date and i.time == time:
            ret = False

    return ret

def seat_taken(t,wid,sid,cid):
    # check if a seat is already taken

    sect = get_sect(t,sid,wid)

    ret = True

    for i in sect.seating:
        if str(cid) == str(i.cid) and i.status != 'available':
            ret = False

    return ret  

def save_order(t,order,patron):
    # move data to appropriate spots when order created
    
    patron.orders.append(order.oid)                             # add oid to patron
    t.patrons.append(patron)                                    # add patron to theater
    t.orders.append(order)                                      # add order to t.orders

    return t

def get_chair(t,cid,sid=None,wid=None):
    # get chair from cid or potentially sid/wid

    if sid and wid:
    
        sect = get_sect(t,sid,wid)

        for i in sect.seating:
            if str(cid) == str(i.cid):
                return i
    else:
        # had to do either this or put sid somewhere inappropriate
        show = get_show(t,wid)
        for i in show.sections:
            for j in i.seating:
                if str(cid) == str(j.cid):
                    return j

def get_seatcount(shows):
    # for reports-seats in show

    count = 0

    for i in shows:
        for j in i.sections:
            for k in j.seating:
                count += 1
    return count

def get_soldseats(shows):
    # for reports-sold seats

    count = 0

    for i in shows:
        for j in i.sections:
            for k in j.seating:
                if str(k.status) == 'sold':
                    count += 1
    return count

def get_revenue(shows):
    # for reports-total revenue

    total = 0

    for i in shows:
        for j in i.sections:
            price = j.price
            for k in j.seating:
                if str(k.status) == 'sold':
                    total = total + price
    return total

def get_sectinfo(sect):
    # for reports-section infomation

    seats_available = 0
    seats_sold = 0
    sect_revenue = 0
    price = sect.price

    for i in sect.seating:
        if i.status == 'sold':
            seats_sold += 1
            sect_revenue = sect_revenue + price
        else:
            seats_available += 1

    return [seats_available,seats_sold,sect_revenue]

def get_donationinfo(t,shows):
    # for reports-donation info

    donated_tickets = 0
    donated_and_used = 0
    donated_value = 0

    for i in shows:

        donated_tickets = donated_tickets + len(i.donations)
        
        for j in i.tickets:

            ticket = get_ticket(t,j.tid)

            if ticket.did and ticket.status == 'used':
                donated_and_used += 1
                donated_value = donated_value + ticket.price
    return [donated_tickets,donated_and_used,donated_value]

def layout_printer(sect,type):
    # for returning theater layout in general or by show

    rows = []
    outrows = []
    seats = []

   # type 1 is for show, type 0 is theater

    for i in range(7):                                              # make 7 rows, can't delete unused, they're placeholders
        rows.append([])            

    for i in sect.seating:
        rows[i.row-1].append(i)        

    for i in range(7):                                              # each row

        if rows[i] != []:

            for j in rows[i]:                                       # each seat in row

                if type == 1:
                    seats.append({'cid':j.cid,'seat':j.snum,'status':j.status})
                else:
                    seats.append(str(j.snum))
            
            outrows.append({'row':i+1,'seats':seats})

            seats = []

    return outrows

def seats_inrow(sect,seat):

    # get all seats in the row

    row = seat.row
    seats = []

    for i in sect.seating:
        if str(i.row) == str(row):
            seats.append(i)
    return seats


def compare_date(start,end,check):
    # check if a date is in a specific range

    # string formatted date YYYYMMDD
    start_year = start[:4]
    start_month = start[4:6]
    start_day = start[6:8]
    start_time = start_year + ' ' + start_month + ' ' + start_day
    start_time = datetime.strptime(start_time,'%Y %m %d')

    end_year = end[:4]
    end_month = end[4:6]
    end_day = end[6:8]
    end_time = end_year + ' ' + end_month + ' ' + end_day
    end_time = datetime.strptime(end_time,'%Y %m %d')

    # datetime formatted date YYYY-MM-DD-TIME
    check_year = check[:4]
    check_month = check[5:7]
    check_day = check[8:10]
    check_time = check_year + ' ' + check_month + ' ' + check_day
    check_time = datetime.strptime(check_time,'%Y %m %d')
    
    if start_time <= check_time and check_time <= end_time:
        return True
    else:
        return False

checked = 0

def seat_blocks(t,show,section,count,seat=None):

    global checked # to count if they've tried a seat

    # front right (123), front left (125): never more than 4
    # main right (126), main left (128): never more than 5
    # front center (124): rows 1-2 have 4, row 3 has 5, row 4 has 6
    # main center (127): row 5 has 6, row 6 has 7, row 7 has 8

    ret = True
    taken = []

    # auto-dq, more seats than the largest in section
    if str(section.sid) == str(123) and \
        int(count) > 4 or str(section.sid) == str(125) and int(count) > 4:
        ret = False
    elif str(section.sid) == str(126) and \
        int(count) > 5 or str(section.sid) == str(128) and int(count) > 5:
        ret = False
    elif str(section.sid) == str(124) and int(count) > 6:
        ret = False
    elif str(section.sid) == str(127) and int(count) > 8:
        ret = False
    if seat:

        row = int(seat.row)

        # check individual rows for max seats
        if str(section.sid) == str(124) and row == 1 and int(count) > 4 or\
            str(section.sid) == str(124) and row == 2 and int(count) > 4 or\
            str(section.sid) == str(124) and row == 3 and int(count) > 5 or\
            str(section.sid) == str(124) and row == 4 and int(count) > 6:

            ret = False

        elif str(section.sid) == str(127) and count > row+1:
            ret = False

        # now check if a seat is taken if no tickets sold, above will catch all
        if len(show.tickets) != 0:
            # check each seat, add to taken if status is 'sold'


            pass
                # below is not working properly-not passing test 14

            for i in section.seating:
                if i.status == 'sold':
                    taken.append((i.cid,i.row))

            inrow = 0

            if len(taken) != 0:
                for i in taken:
                    if i[1] == row:
                        inrow += 1  # count how many seats are taken in the row

            if inrow > 0:
                # there is at least one seat taken in the row
                # so instead of subtracting available (difficult at this point)
                # reiterate with more seats to see if it's disqualified
                # DOES NOT account if seat is taken in the middle,
                # the logic being that the others could ask to trade seats

                seat_blocks(t,show,section,int(count)+int(inrow),section.seating[checked])

    if ret and not seat:
        # has passed all tests, and they didn't send a seat
        # send first seat in section

        if checked == 0:
            ret = section.seating[checked]
            checked += 1
        else:
            for i in section.seating:
                if str(i.row) != section.seating[0].row:
                    ret = i

    elif ret and seat:
        # has passed all tests, send back seat
        ret = seat

    return ret
