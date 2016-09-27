# -*- coding: utf-8 -*-
import ftplib
import os
import threading


class downloaderThread(threading.Thread):
    def __init__(self, threadID, directories, ftp,  lookfor, path, localpath):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.directories = directories
        self. lookfor = lookfor
        self.ftp = ftp
        self.path = path
        self.localpath = localpath

    def run(self):
        # different ftp connections are needed for each thread. sad
        print "[!] Starting thread {0}".format(self.threadID)
        for directory in self.directories:
            try:
                print "[!] ", self.ftp.pwd(), " ", self.threadID
                self.ftp.cwd(directory)
                print "Success changind directory to {0} [{1}]".format(self.ftp.pwd(), self.threadID)
                files = self.ftp.nlst()

                for file in files:
                    if self.lookfor in file:
                        print "[!] Match found [{0}] : {1}".format(self.threadID, file)

                self.ftp.cwd("..")
                print "[!] success changing directory to .. [{0}]".format(self.threadID)
            except Exception as e:
                print "[-] Error [{0}]: {1}".format(str(e.args), self.threadID)


def download(ftp, remotefile, localpath, name):  # This function will download the file at path in localpath + os.sep + name of file
    if not os.path.isdir(localpath):
        os.makedirs(localpath)

    try:
        localfile = open(localpath + os.sep + name + remotefile[-4:], 'wb')   # remotefile[-4:] sets the extension
        try:
            print "[+] Downloading file " + remotefile
            ftp.retrbinary("RETR " + remotefile, localfile.write)
            print "[!] Downloading comeplete -> " + remotefile
        except Exception as e:
            print "[-] Error downloading file: " + str(e.args)
    except Exception as e:
        print "[-] Error opening file: " + str(e.args)

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


def main():

    addr = '128.138.97.102'  # This is the address of ftp://n5eil01u.ecs.nsidc.org/SAN/MOST/MOD10A2.006. Retrieved from Filezilla
    password = user = 'anonymous'

    ftp = ftplib.FTP(addr)
    ftp.login(user, password)

    response = ftp.cwd("MOST/MOD10A2.006/")
    print response

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

    t1 = downloaderThread(1, directories[0:10], ftp, "h25v06", "ff", "")
    t2 = downloaderThread(2, directories[10:20], ftp, "gggg", "ff", "")

    t1.start()
    t2.start()




if __name__ == '__main__':
    main()