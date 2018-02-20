import theater_classes as tc

def get_cid(row,seat):

    mods = [0,12,24,37,51,67,84]

    for i in range(1,8):
        
        if row == i:
            cid = 200 + seat + mods[i-1]
    return cid

    # below is old, row/seat numbering system
    # which is logical but wanted to follow example

#    if int(seat) < 10:

#        seat = '0' + str(seat)

#    return str(row)+str(seat)

def create_theater():

    sections = []
    tempseats = []

    for i in range(1,5):
        for j in range(1,5):
        
            tempseats.append(tc.seat(i,j,get_cid(i,j),'123'))
            
    s1 = tc.section(0,"123","Front right")
    s1.seating = tempseats
    sections.append(s1)
    tempseats = []

    for i in range(5,8):
        for j in range(1,6):
        
            tempseats.append(tc.seat(i,j,get_cid(i,j),'126'))
            
    s2 = tc.section(0,"126","Main right")
    s2.seating = tempseats
    sections.append(s2)
    tempseats = []

    for i in range(1,5):
        for j in range(5,9):       
        
            tempseats.append(tc.seat(i,j,get_cid(i,j),'124'))
            
    s3 = tc.section(0,"124","Front center")

    for i in range(3,5):
        tempseats.append(tc.seat(i,9,get_cid(i,9),'124'))
    tempseats.append(tc.seat(4,10,get_cid(4,10),'124'))

    s3.seating = tempseats
    sections.append(s3)
    tempseats = []

    for i in range(5,8):
        for j in range(6,12):       
        
            tempseats.append(tc.seat(i,j,get_cid(i,j),'127'))
            
    s4 = tc.section(0,"127","Main center")

    for i in range(6,8):
        tempseats.append(tc.seat(i,12,get_cid(i,12),'127'))
    tempseats.append(tc.seat(7,13,get_cid(7,13),'127'))

    s4.seating = tempseats
    sections.append(s4)
    tempseats = []

    s5 = tc.section(0,"125","Front left")

    for i in range(1,3):
        for j in range(9,13):        
        
            tempseats.append(tc.seat(i,j,get_cid(i,j),'125'))

    for i in range(10,14):
        
            tempseats.append(tc.seat(3,i,get_cid(3,i),'125'))

    for i in range(11,15):
    
        tempseats.append(tc.seat(4,i,get_cid(4,i),'125'))

    s5.seating = tempseats
    sections.append(s5)
    tempseats = []

    s6 = tc.section(0,"128","Main left")

    for i in range(12,17):
        tempseats.append(tc.seat(5,i,get_cid(5,i),'128'))


    for i in range(13,18):
        
            tempseats.append(tc.seat(6,i,get_cid(6,i),'128'))

    for i in range(14,19):
    
        tempseats.append(tc.seat(7,i,get_cid(7,i),'128'))

    s6.seating = tempseats
    sections.append(s6)
    tempseats = []

    t = tc.theater(sections)
    t.reports = [tc.reports(801,"Theater occupancy"),\
        tc.reports(802,"Revenue from ticket sales"),\
        tc.reports(803,"Donated tickets report")]

    return t
