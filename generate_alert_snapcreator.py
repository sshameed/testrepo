#!/usr/local/bin/python3
import os
import glob
import time
import pathlib
import smtplib



##############################################
def find_log_files_with_error(lista):
    #print("debug, lista",lista)
    #print("list of files:")
    print("debug 1")
    print(lista)
    var=[]
    for i in lista:
        var = var + glob.glob(i + "???_*out*log")
        print(var)

    #print("debug: filelist")
    #print(var)

    #for i in var.split():
    #    print("file:",i)

    log_files_with_error = []
    # get current time
    currenttime=time.time()

    for filename in var:
        #        print("debug: filename:",filename)
# check if file is modified less than threshold (1 hour)
        mtime1=os.stat(filename).st_mtime
        #if (currenttime-mtime1 > 3600*10000):
        if (currenttime-mtime1 <= 3600):
            pass
        else:
            continue        
    
        found = "False"
        try:
            with open(filename, 'rt') as myfile:
                for myline in myfile:
                    if 'ERROR:' in myline:
                        found = "True"
        except:
            print("error: unable to open", filename)
        if (found == "True"):
            log_files_with_error.append(str(filename))
    return(log_files_with_error)

##############################################
def update_notification_file(sid,notification_file):
    
    currenttime = str(time.time())
    try:
        with open(notification_file, "a") as f:
            var1 = sid + "," + currenttime + '\n'
            f.write(var1)
    except:
        print("error: unable to open", notification_file)


##############################################
def get_sid_name_from_log_file(logfile):
    tmpa  = logfile.split('/')[-1]
    sid = tmpa.split('_')[0]
    return(sid)

##############################################
def check_entry_in_file(sid,notification_file):
    try:
        found = "False"
        with open(notification_file, "rt") as f:
            for line in f:
                if sid in line:
                    found = "True"
    except:
        print("error: unable to open", notification_file)

    if (found == "False"):
        return "False"

    if (found == "True"):
        # else check whether last notification was sent before threshold (30 minutes)
        # find last entry matching sid
        lastmatch = "dummy"
        with open(notification_file, "rt") as f:
            for line in f:
                if sid in line:
                    lastmatch = line
        if (lastmatch == "dummy"):
            return "False"

        # get last match time
#        print("debug - check_entry_in_file - , select line:", lastmatch)
        matchtime = float(lastmatch.split(',')[1])
#        print("last updated timestamp:", matchtime)
        currenttime = time.time()
#        print("time difference in seconds since last update:", currenttime - matchtime)

        # threshold= 1800 seconds (30 minutes)
        if (currenttime - matchtime >= 1800 ):
#            print("generate alert and update notification file.")
            return "Expired"
        else:
            return "True"

##############################################
def send_email(subject,msglist):

    to_addrs = [ "test@abc.com", "test@null.com", "test@testing.org" ]
    # convert message list to a string with messages separated by new line
    msg = "Subject: " + "Fujitsu alert, snapcreator: " + subject + "\n\n"
    for i in msglist:
        msg += i

    server = smtplib.SMTP('172.16.109.123',25)
    server.sendmail("me@test.com",to_addrs,msg)
    server.quit()


##############################################
def generate_alert(sid,log_files_with_error):
    # for each sid, get log file with error
    print("inside function generate_alert for sid",sid)
    log_files_sid = []
    for i in log_files_with_error:
        if sid in i:
            log_files_sid.append(i)
    # look for string ERROR: in each log file

    errorstring = []
    for i in log_files_sid:
        try:
            with open(i, 'rt') as myfile:
                for myline in myfile:
                    if 'ERROR:' in myline:
                        found = "True"
                        errorstring.append(myline)
        except:
            print("error: unable to open", filename)
    print("message body for sid: ", sid)
    for i in errorstring:
        print(i)
    send_email(sid,errorstring)


## main

notification_file="/tmp/notification"

# update log_dir_list with all directories with snapcreator log files
log_dir_list = [ "/usr/local/scServer/engine/logs/VPS_snap_local/", "/usr/local/scServer/engine/logs/VPS_remote_snapmirror/", "/usr/local/scServer/engine/logs/VBR_snap_local", "/usr/local/scServer/engine/logs/VBR_remote_snapmirror/" ]


log_files_with_error = []
log_files_with_error = find_log_files_with_error(log_dir_list)
# debug
#print("log files with error:")
#for i in log_files_with_error:
#    print(i)
# end debug
sid_list = []
for i in log_files_with_error:
    sid = get_sid_name_from_log_file(i)
    sid_list.append(sid)

# remove duplicates from sid list
t1 = list(set(sid_list))
sid_list = t1
# print all SIDs with error
print(sid_list)

print("looping through sids")
for sid in sid_list:
    print("sid:",sid)
    result = check_entry_in_file(sid,notification_file)
    print("result for sid",sid, "is", result)
    if (result == "True"):
        print("entry for",sid,"present.")
    elif (result == "False"):
        print("entry for",sid,"NOT present.")
        generate_alert(sid,log_files_with_error)
        update_notification_file(sid,notification_file)
    elif (result == "Expired"):
        print("entry for",sid,"is expired.")
        generate_alert(sid,log_files_with_error)
        update_notification_file(sid,notification_file)
