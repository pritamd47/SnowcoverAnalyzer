# -*- coding: utf-8 -*-
import ftplib
import os
from datetime import date

def download(ftp, path, localpath, lookfor):
    # Downloads files from every directory which contains 'lookfor' in them.

    try:
        res = ftp.cwd(path)
        print "[+] " + res           # Changing current working directory to path  [FTP]
    except Exception as e:
        print e.args

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
    # Now directories list contains only folder names

    if not os.path.exists(path):
        os.makedirs(path)
        print "[+] Creating directory: " + localpath

    for folder in directories:

        print "[!] Current folder: " + folder
        try:
            res = ftp.cwd(folder)
        except:
            continue
        files = ftp.nlst()

        os.makedirs(localpath + os.sep + folder)

        for file in files:
            if lookfor in file:
                # Required match found, download in respective folder and file
                print "[+] Match Found: " + file
                filename = lookfor + "." + file[-3:]         # filename wil be lookfor + ".xml" / ".hdf", whatever the extension
                localfile = open(localpath + os.sep + folder + os.sep + filename, 'wb')
                try:
                    print "[+] Downloading file"
                    ftp.retrbinary("RETR " + file, localfile.write)
                    print "[!] Download Successful!"
                except Exception as e:
                    print "[-] " + str(e.args)

                localfile.close()
        ftp.cwd('..')
def main():

    addr = '128.138.97.102'  # This is the address of ftp://n5eil01u.ecs.nsidc.org/SAN/MOST/MOD10A2.006. Retrieved from Filezilla
    password = user = 'anonymous'

    FTP = ftplib.FTP(addr)
    FTP.login(user, password)

    download(FTP, "/SAN/MOST/MOD10A2.006","Data","h25v06")


if __name__ == '__main__':
    main()