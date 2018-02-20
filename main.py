import theater_classes as tc
import theater_helpers as th
import pickle
import theater_setup
import sys
import os
import uuid
from flask import Flask,jsonify,json,request,abort

# file handling

def saveme():
    pickle.dump(t,open('theater_save.p','wb'))                                          # saves theater

def resetme():                                                                          # to delete saved file
    os.remove('theater_save.p')

if os.path.exists('theater_save.p'):				                                    # for persistance
    t = pickle.load(open('theater_save.p','rb'))

else:
    t = theater_setup.create_theater()                                                  # no save,new theater
    saveme()

# end file handling

app = Flask(__name__)

@app.route('/thalia/shows',methods=['GET','POST'])

def shows_no_wid():

    if request.method == 'POST':
        # create show

        data = request.get_json()                                                       # get data
                                                       
        if not th.verifier(data,'show_info',['name','date','time']):
            return abort(400)                                                           # bad request
        else:
            name = data['show_info']['name']                                            # get data from json
            date = data['show_info']['date']
            time = data['show_info']['time']

            if not th.dupe_show(t,date,time):                                           # check for dupe show
                return abort(400)

            if 'web' not in data['show_info']:                                          # check for optionals
                web = None
            else:
                web = data['show_info']['web']
            
            if 'wid' not in data['show_info']:
                wid = uuid.uuid4()
            else:
                wid = int(data['show_info']['wid'])

            t.shows.append(tc.show(name,date,time,web,wid))                             # add show to theater

            s = th.get_show(t,wid)

            for i in data['seating_info']:                                              # could technically use t.shows[-1]
                                                                                        # this way to avoid race condition
                if 'sid' in i:

                    sid = i['sid']                                                      # pull sections from data
                    price = i['price']

                    newsect = None

                    for i in t.sections:                                                # find/copy section from template
                        if i.sid == sid:
                            newsect = i

                    newsect.price = price                                               # adjust price

                    s.sections.append(newsect)
                else:
                    return abort(400)                                                   # means no sid

            saveme()
            return jsonify({'wid':s.wid})                                               # return wid

    else:
        # return all shows

        ret = []
        for i in t.shows:
            ret.append({'wid':str(i.wid),\
                'show_info':{'name':i.name,'web':i.web,'date':i.date,'time':i.time}})
        
        return jsonify(ret)

@app.route('/thalia/shows/<wid>',methods=['GET','PUT'])

def shows_with_id(wid):

    s = th.get_show(t,wid)

    if request.method == 'PUT':
        # change show info

        data = request.get_json()
                                                        
        if not th.verifier(data,'show_info',['name','date','time']):

            return abort(400)                                                           # bad request

        else:
            name = data['show_info']['name']                                            # get data from json
            date = data['show_info']['date']
            time = data['show_info']['time']

            for i in data['seating_info']:                                              # search data for new section info
                if 'sid' in i:
                    for j in s.sections:
                        if j.sid == i['sid']:
                            j.price = i['price']                                        # update price
                else:
                    return abort(400)                                                   # means no sid

            saveme()
            return ('',200)                                                             # no response

    else:
        # return info on show wid

        sects = []

        for i in s.sections:
            sects.append({'sid':i.sid,'price':i.price})

        ret = {'wid':str(s.wid),'show_info':{'name':s.name,'web':s.web,'date':s.date,\
            'time':s.time},'seating_info':sects}

        return jsonify(ret)

@app.route('/thalia/shows/<wid>/sections')

def sections_for_show(wid):
    # get all sections for show

    s = th.get_show(t,wid)
    sects = []

    for i in s.sections:
        sects.append({'sid':i.sid,'section_name':i.name,'price':i.price})

    return jsonify(sects)

@app.route('/thalia/shows/<wid>/sections/<sid>')

def sections_for_show_specific(wid,sid):
    # get specific section for show

    s = th.get_show(t,wid)
    sect = th.get_sect(t,sid,wid)

    outrows = th.layout_printer(sect,1)

    section_info = {'wid':str(s.wid),\
        'show_info':{'name':s.name,'web':s.web,'date':s.date,'time':s.time},\
        'sid':sect.sid,'section_name':sect.name,'price':sect.price,'seating':outrows}

    return jsonify(section_info)

@app.route('/thalia/shows/<wid>/donations',methods=['POST'])

def request_donation(wid):
    # request donated ticket

    global t            # t is changed in this section

    data = request.get_json()

    tic_count = data['count']                                                       # get ticket count from data
    did = uuid.uuid4()                                                              # generate did
    s = th.get_show(t,wid)                                                          # get show

    newpatron = th.create_patron(data)                                              # create patron
    neworder = tc.order(tic_count,newpatron.pid,wid,0,did,'pending')                # create order
    s.donations_wait.append(did)
    t = th.save_order(t,neworder,newpatron)                                         # save order
    saveme()
    return jsonify({'did':did})

@app.route('/thalia/shows/<wid>/donations/<did>')

def show_donations(wid,did):
    # get status of donation for show

    order = th.get_order(t,None,did)
    cust = th.get_patron(t,order.pid)

    ret = {'did':order.did,'wid':order.wid,'count':order.count,\
        'status':order.status,'tickets':order.tickets,\
        'patron_info':{'name':cust.name,'phone':cust.phone,'email':cust.email,\
        'billing_address':cust.billing_address,'cc_number':cust.cc_number,\
        'cc_expiration_date':cust.cc_expiration_date}}

    return jsonify(ret)

@app.route('/thalia/seating')

def get_seating():

    # check for seats with options

    wid = request.args.get('show', None)                                            # kwargs
    sid = request.args.get('section', None)  
    count = request.args.get('count', None)
    seats = request.args.get('starting_seat_id', None)

    if wid:
        seats = th.get_chair(t,seats,sid,wid)                                       # for specific show
        show = th.get_show(t,wid)
        sect = th.get_sect(t,sid,wid)

        checker = th.seat_blocks(t,show,sect,count,seats)

        if not checker:
            # block not available
            cid = None
            status = 'Error: '+str(count)+' contiguous seats not available'
            seating = []

            ret = {'wid':wid,'show_info':{'name':show.name,'web':show.web,\
                'date':show.date,'time':show.time},'sid':sid,'section_name':sect.name,\
                'starting_seat_id':cid,'status':status,'seating':seating} 
        else:
            total = int(sect.price) * int(count)
            status = 'ok'

            seating = []

            seats_in_row = th.seats_inrow(sect,checker)

            for i in seats_in_row:
                seating.append({'cid':i.cid,'seat':i.snum,'status':i.status})

            ret = {'wid':wid,'show_info':{'name':show.name,'web':show.web,\
                'date':show.date,'time':show.time},'sid':sid,'section_name':sect.name,\
                'starting_seat_id':checker.cid,'status':status,\
                'total_amount':total,'seating':seating} 

    else:
        # get all seats in theater (no options)

        ret = []
        
        for i in t.sections:
            ret.append({'sid':i.sid,'section_name':i.name})

    return jsonify(ret)

@app.route('/thalia/seating/<sid>')

def get_seating_section(sid):
    # get all seats in theater by sid

    sect = th.get_sect(t,sid)
    outrows = th.layout_printer(sect,0)                                                 # see theater_helpers for details

    ret = {'sid':sect.sid,'section_name':sect.name,'seating':outrows}

    return jsonify(ret)

@app.route('/thalia/orders',methods=['GET','POST'])

def place_order():

    global t    # t is changed in this section

    if request.method == 'POST':
        # place order

        data = request.get_json()

        tic_count = len(data['seats'])
        wid = data['wid']
        sid = data['sid']
        s = th.get_show(t,wid)
        sect = th.get_sect(t,sid,wid)
        cost = sect.price
        total = int(cost) * tic_count

        newpatron = th.create_patron(data)
        neworder = tc.order(tic_count,newpatron.pid,wid,total)

        tix = []
        for i in data['seats']:                                                         # get seats
            if th.seat_taken(t,wid,sid,i['cid']):                                       # check if seat is taken (true is good)

                chair = th.get_chair(t,i['cid'],sid,wid)                                # get seat
                ticket = tc.ticket(cost,wid,chair.cid,neworder.oid)                     # generate ticket
                chair.status = 'sold'                                                   # change to sold
                tix.append(ticket)
                s.tickets.append(ticket.tid)

        neworder.tickets = tix

        t = th.save_order(t,neworder,newpatron)                                         # made this sub to save space 
        saveme()                                                                        # but caused me to have to use global var

        ret_tix = []

        for i in tix:

            ret_tix.append(i.tid)

        ret = {'oid':neworder.oid,'wid':wid,'show_info':{'name':s.name,'web':s.web,\
            'date':s.date,'time':s.time},'date_ordered':neworder.time,\
            'order_amount':neworder.total,'tickets':ret_tix}

        return jsonify(ret)

    else:
        # get all orders or orders by date

        start = request.args.get('start_date', None)
        end = request.args.get('end_date', None)  
        dateflag = 0

        if start:                                                                       # kwargs include dates
            dateflag = 1

        ret = []

        for i in t.orders:

            num_tix = i.count
            wid = i.wid
            patron = th.get_patron(t,i.pid)
            show = th.get_show(t,i.wid)
    
            rets = {'oid':i.oid,'wid':i.wid,'show_info':{'name':show.name,'web':show.web,\
            'date':show.date,'time':show.time},'date_ordered':i.time,'order_amount':i.total,\
            'number_of_tickets':num_tix,\
            'patron_info':{'name':patron.name,'phone':patron.phone,'email':patron.email,\
            'billing_address':patron.billing_address,'cc_number':patron.cc_number,\
            'cc_expiration_date':patron.cc_expiration_date}}

            if not dateflag:
                ret.append(rets)                                                        # no dates, append all

            elif th.compare_date(start,end,i.time):                                     # has dates, this is within range
                ret.append(rets)

        return jsonify(ret)

@app.route('/thalia/orders/<oid>')

def get_orders(oid):
    # get order by oid

    order = th.get_order(t,oid)

    ret_tix = []
    num_tix = len(order.tickets)

    for i in order.tickets:
        ret_tix.append({'tid':i.tid,'status':i.status})

    wid = order.wid
    s = th.get_show(t,wid)
    this_patron = th.get_patron(t,order.pid)    

    ret = {'oid':order.oid,'wid':order.wid,'show_info':{'name':s.name,'web':s.web,\
            'date':s.date,'time':s.time},'date_ordered':order.time,'order_amount':order.total,\
            'number_of_tickets':num_tix,\
            'patron_info':{'name':this_patron.name,'phone':this_patron.phone,'email':this_patron.email,\
            'billing_address':this_patron.billing_address,'cc_number':this_patron.cc_number,\
            'cc_expiration_date':this_patron.cc_expiration_date},'tickets':ret_tix}

    return jsonify(ret)

@app.route('/thalia/tickets/<tid>',methods=['GET','POST'])

def tickets(tid):

    if request.method == 'POST':
        # scan ticket

        data = request.get_json()

        tid = data['tid']
        status = data['status']

        this_ticket = th.get_ticket(t,tid)

        if this_ticket.status == 'used':                                                # ticket has already been used
            return abort(400)
        else:
            this_ticket.status = status

        saveme()
        return jsonify({'tid':this_ticket.tid,'status':this_ticket.status})

    else:
        # get ticket info

        ticket = th.get_ticket(t,tid)                                                   # because of compartmentalized data
        show = th.get_show(t,ticket.wid)                                                # this was surprisingly difficult
        order = th.get_order(t,ticket.oid)
        patron = th.get_patron(t,order.pid)
        seat = th.get_chair(t,ticket.cid,None,show.wid)
        section = th.get_sect(t,seat.sid)
        
        ret = {'tid':ticket.tid,'price':ticket.price,'status':ticket.status,\
            'wid':show.wid,'show_info':{'name':show.name,'web':show.web,\
            'date':show.date,'time':show.time},'patron_info':{'name':patron.name,\
            'phone':patron.phone,'email':patron.email,\
            'billing_address':patron.billing_address,'cc_number':patron.cc_number,\
            'cc_expiration_date':patron.cc_expiration_date},'sid':seat.sid,\
            'section_name':section.name,'seating':[{'row':seat.row,\
            'seats':[{'cid':seat.cid,"seat":seat.snum}]}]}

        return jsonify(ret)

@app.route('/thalia/tickets/donations',methods=['POST'])

def donate_ticket():
    # donate unused ticket

    data = request.get_json()
    tickets = data['tickets']

    # add ticket to show.donations

    if tickets:
        ticket = th.get_ticket(t,tickets[0])
        show = th.get_show(t,ticket.wid)
    else:
        return abort(400)

    for i in tickets:

        show.donations.append(i)

    for i in show.donations_wait:                                                       # check tickets from donations_wait

        order = th.get_order(t,None,i)                                                  # get order from did
        count = order.count                                                             # check count
        if len(order.tickets) < count and order.did:                                    # if len(order.ticket) and did
            for j in show.donations:                                                    #check each ticket in donations
                dticket = th.get_ticket(t,j)
                if dticket.status == 'Open' and len(order.tickets) < count:             # for validity
                    order.tickets.append(dticket.tid)                                   # add tid to new order, mark as donated
                    dticket.status = 'Donated'                                          # list ticket status as donated
        if order.count == len(order.tickets):                                           # order is complete
            order.status = 'assigned'

    return ('',201)

@app.route('/thalia/reports')

def list_reports():
    # get list of reports

    ret = []

    for i in t.reports:
        ret.append({'mrid':i.mrid,'name':i.name})                                       # this was in case adding more reports

    return jsonify(ret)

@app.route('/thalia/reports/<mrid>')

def get_reports(mrid):
    # get various reports

    wid = request.args.get('show', '')
    start = request.args.get('start_date', '')
    end = request.args.get('end_date', '')

    shows = []

    if not wid and not start and not end:
    # no show and no dates, run for all shows and all dates
        
        for i in t.shows:
            shows.append(i)

    if wid and not start and not end:
    # show and no dates, run for that show 
        
        shows.append(th.get_show(t,wid))

    if not wid and start and end:
    # if no show and dates, run for all shows in that range
                
        for i in t.shows:
            if th.compare_date(start,end,i.date):                                       # check for dates

                shows.append(i)

    if str(mrid) == str(801):
        name = "Occupancy Report"
        total_shows = len(shows)            
        total_seats = th.get_seatcount(shows)
        sold_seats = th.get_soldseats(shows)

        overall_occupancy = str(round((sold_seats/total_seats)*100,1))+'%'
        
        rets = []

        for i in shows:
            seats_sold = th.get_soldseats([i])
            total_seat = th.get_seatcount([i])                                          # scoping shouldn't be a problem but...
            seats_available = total_seat-seats_sold
            occupancy = str(round((seats_sold/seats_available)*100,1))+'%'              # could check for div/0
            rets.append({'wid':i.wid,'show_info':{'name':i.name,'web':i.web,\
            'date':i.date,'time':i.time},'seats_available':seats_available,\
            'seats_sold':seats_sold,'occupancy':occupancy})

        ret = {'mrid':mrid,'name':name,'start_date':start,'end_date':end,\
            'total_shows':total_shows,'total_seats':total_seats,\
            'sold_seats':sold_seats,'overall_occupancy':overall_occupancy,\
            'shows':rets}

    elif str(mrid) == str(802):
        name = "Revenue from ticket sales"
        total_shows = len(shows)
        total_seats = th.get_seatcount(shows)
        sold_seats = th.get_soldseats(shows)

        overall_revenue = th.get_revenue(shows)

        rets = []
        rets2 = []

        for i in shows:
            for j in i.sections:
                sectinfo = th.get_sectinfo(j)
                seats_available = sectinfo[0]                                           # added these separately for transparency
                seats_sold = sectinfo[1]                                                # originally just had in return value
                section_revenue = sectinfo[2]

                rets2.append({'sid':j.sid,'section_name':j.name,\
                'section_price':j.price,'seats_available':seats_available,\
                'seats_sold':seats_sold,'section_revenue':section_revenue})

            rets.append({'wid':i.wid,'show_info':{'name':i.name,'web':i.web,\
            'date':i.date,'time':i.time},'sections':rets2})
            rets2 = []

        ret = {'mrid':mrid,'name':name,'start_date':start,'end_date':end,\
            'total_shows':total_shows,'total_seats':total_seats,\
            'sold_seats':sold_seats,'overall_revenue':overall_revenue,\
            'shows':rets}

    elif str(mrid) == str(803):
        name = "Donated Tickets Report"
        total_shows = len(shows)
        total_seats = th.get_seatcount(shows)
        sold_seats = th.get_soldseats(shows)

        donation_info = th.get_donationinfo(t,shows)
        donated_tickets = donation_info[0]
        donated_and_used_tickets = donation_info[1]
        donated_and_used_value = donation_info[2]

        rets = []

        for i in shows:
            seats_sold = th.get_soldseats([i])
            total_seat = th.get_seatcount([i])
            seats_available = total_seat-seats_sold

            di = th.get_donationinfo(t,[i])
            donated_ticket = di[0]
            donated_and_used_ticket = di[1]
            donated_and_used_val = di[2]

            rets.append({'wid':i.wid,'show_info':{'name':show.name,'web':show.web,\
            'date':show.date,'time':show.time},'seats_available':seats_available,\
            'seats_sold':seats_sold,'donated_tickets':donated_ticket,\
            'donated_and_used_tickets':donated_and_used_ticket,\
            'donated_and_used_value':donated_and_used_val})

        ret = {'mrid':mrid,'name':name,'start_date':start,'end_date':end,\
            'total_shows':total_shows,'total_seats':total_seats,\
            'sold_seats':sold_seats,'donated_tickets':donated_tickets,\
            'donated_and_used_tickets':donated_and_used_tickets,\
            'donated_and_used_value':donated_and_used_value,\
            'shows':rets}

    else:
        return abort(404)                                                               # invalid report code

    return jsonify(ret)

@app.route('/thalia/search')

def serch():

    # search for shows or orders, misspelled search on purpose

    topicword = request.args.get('topic', None)
    keyword = request.args.get('key', None)
    keyword = keyword.upper()                                           # remove case sensitivity problem, works on all strings

    ret = None

    if topicword == 'show':

        for i in t.shows:

            # show name, web, date, time
            if keyword in str(i.name).upper() or \
                keyword in str(i.web).upper or \
                keyword in str(i.date) or keyword in str(i.time):

                ret = {'wid':i.wid,'show_info':{'name':i.name,'web':i.web,\
                    'date':i.date,'time':i.time}}

        return jsonify(ret)

    elif topicword == 'order':

        for i in t.orders:

            patron = th.get_patron(t,i.pid)
            show = th.get_show(t,i.wid)

            # oid, sid, pid, patron name, patron phone, patron email, patron address
            if keyword in str(i.oid).upper() or keyword in str(i.wid).upper() or \
                keyword in str(patron.pid).upper() or keyword in patron.name.upper() or \
                keyword in str(patron.phone) or keyword in patron.email.upper() or \
                keyword in patron.billing_address.upper():

                ret = {'oid':i.oid,'wid':i.wid,'show_info':{'name':show.name,'web':show.web,\
                    'date':show.date,'time':show.time},'date_ordered':i.time,'order_amount':i.total,\
                    'number_of_tickets':i.count,\
                    'patron_info':{'name':patron.name,'phone':patron.phone,'email':patron.email,\
                    'billing_address':patron.billing_address,'cc_number':patron.cc_number,\
                    'cc_expiration_date':patron.cc_expiration_date}}

        return jsonify(ret)
    else:
        return abort(404)

