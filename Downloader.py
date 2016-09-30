# -*- coding: utf-8 -*-
import ftplib
import os
import threading
import time


class downloaderThread(threading.Thread):
    def __init__(self, threadID, directories, lookfor, path, localpath):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.directories = directories
        self. lookfor = lookfor
        self.path = path
        self.localpath = localpath

    def connecttoftp(self, addr, username = 'anonymous', password = 'anonymous'):
        try:
            print "[+][{threadid}] Trying to connect: {0} with username: {1} , password: {2}".format(addr, username, password, threadid=self.threadID)
            self.ftp = ftplib.FTP(addr)
            self.ftp.login(username, password)
            print "[+][{threadid}] Connected".format(threadid=self.threadID)
            self.ftp.cwd(self.path)

        except Exception as e:
            print "[-][{threadid}] Failed to connect to ftp server: {0}".format(e.args, threadid=self.threadID)

    def run(self):

        print "[!][{0}] Starting thread ".format(self.threadID)
        for directory in self.directories:
            try:
                self.ftp.cwd(directory)
                # changed directory to directory passed
                files = self.ftp.nlst()

                for file in files:
                    if self.lookfor in file:
                        print "[!][{0}] Match found : {1}".format(self.threadID, file)
                        download(self.ftp, file, self.localpath + os.sep + directory + os.sep, self.lookfor, self.threadID)


                self.ftp.cwd("..")
            except Exception as e:
                print "[-] Error [{0}]: {1}".format(str(e.args), self.threadID)
        callbackme()

        self.ftp.quit()



def download(ftp, remotefile, localpath, name, threadid = -1):  # This function will download the file at path in localpath + os.sep + name of file
    if not os.path.isdir(localpath):
        os.makedirs(localpath)

    try:
        localfile = open(localpath + os.sep + name + remotefile[-4:], 'wb')   # remotefile[-4:] sets the extension
        try:
            print "[+][{0}] Downloading file ".format(threadid) + remotefile
            ftp.retrbinary("RETR " + remotefile, localfile.write)
            print "[!][{0}] Downloading comeplete -> ".format(threadid) + remotefile
        except Exception as e:
            print "[-][{0}] Error downloading file: ".format(threadid) + str(e.args)
    except Exception as e:
        print "[-][{0}] Error opening file: ".format(threadid) + str(e.args)

# def download(ftp, path, localpath, lookfor):
#     # Downloads files from every directory which contains 'lookfor' in them.
#
#     try:
#         res = ftp.cwd(path)
#         print "[+] " + res           # Changing current working directory to path  [FTP]
#     except Exception as e:
#         print e.args
#
    # directories = []
    # ftp.retrlines('MLSD', directories.append)  # save names of directories in this directories list  [FTP]
    #
    # # extract just the directory names
    # for i in range(len(directories)):
    #     elem = directories[i]
    #     if "dir" in elem:
    #         elem = (elem.split(";")[-1]).strip(" ")
    #         directories[i] = elem
    #     else:
    #         directories[i] = None
    #
    # directories = filter(None, directories)
    # print "[+] Directory names extracted"
    # directories.remove('.')
    # directories.remove('..')
    # directories.sort()
#
#     # Now directories list contains only folder names
#
#     if not os.path.exists(path):
#         os.makedirs(path)
#         print "[+] Creating directory: " + localpath
#
#     for folder in directories:
#
#         print "[!] Current folder: " + folder
#         try:
#             res = ftp.cwd(folder)
#         except:
#             continue
#         files = ftp.nlst()
#
#         os.makedirs(localpath + os.sep + folder)
#
#         for file in files:
#             if lookfor in file:
#                 # Required match found, download in respective folder and file
#                 print "[+] Match Found: " + file
#                 filename = lookfor + "." + file[-3:]         # filename wil be lookfor + ".xml" / ".hdf", whatever the extension
#                 localfile = open(localpath + os.sep + folder + os.sep + filename, 'wb')
#                 try:
#                     print "[+] Downloading file"
#                     ftp.retrbinary("RETR " + file, localfile.write)
#                     print "[!] Download Successful!"
#                 except Exception as e:
#                     print "[-] " + str(e.args)
#
#                 localfile.close()
#         ftp.cwd('..')

def callbackme():
    global directoriesleft, lock
    lock.acquire()
    try:
        directoriesleft -= 1
    finally:
        lock.release()

def threadhandler(tot_directories, max_threads, lookfor, path, localpath, thread_cap = 10):
    latest_directory = 0
    global directoriesleft, lock

    lock = threading.Lock()
    #dividing total directories into tuples of sections

    total_directories = []
    length = len(tot_directories)
    i = 0
    while i <= (length):
        total_directories.append(tuple(tot_directories[i:i+thread_cap]))
        i += thread_cap

    # total_directories now contain tuples which can be passed into threads to download

    directoriesleft = len(total_directories)
    threadid = 0
    threads = []
    i = 0
    while True:
        if directoriesleft:
            if threading.activeCount() < max_threads:
                thread = downloaderThread(i, total_directories[i], lookfor, path, localpath)
                thread.connecttoftp('128.138.97.102')
                thread.start()
                i += 1
                #time.sleep(0.5)
                threads.append(thread)
            else:
                continue
        else:
            break


def main():

    addr = '128.138.97.102'  # This is the address of ftp://n5eil01u.ecs.nsidc.org/SAN/MOST/MOD10A2.006. Retrieved from Filezilla
    password = user = 'anonymous'

    ftp = ftplib.FTP(addr)
    ftp.login(user, password)

    response = ftp.cwd("MOST/MOD10A2.006/")

    directories = []
    ftp.retrlines('MLSD', directories.append)  # save names of directories in this directories list  [FTP]

    # extract just the directory names
    for i in range(len(directories)):
        elem = directories[i]
        if "dir" in elem:
            elem = (elem.split(";")[-1]).strip(" ")
            directories[i] = elem
        else:
            directories[i] = None

    directories = filter(None, directories)
    print "[+] Directory names extracted"
    directories.remove('.')
    directories.remove('..')
    directories.sort()


    threadhandler(directories, 10, "h25v06", "MOST/MOD10A2.006/", "Data\\", thread_cap= 10)


    # t1 = downloaderThread(1, directories[0:10], "h25v06", "MOST/MOD10A2.006/", "Data\\")
    # t2 = downloaderThread(2, directories[10:20], "h25v06", "MOST/MOD10A2.006/", "Data\\")
    #
    # t1.connecttoftp(addr)
    # t2.connecttoftp(addr)
    # t1.start()
    # t2.start()


if __name__ == '__main__':
    main()