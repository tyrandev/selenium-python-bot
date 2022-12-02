from time import sleep
import requests # package pour verifier la connection internet # pip instal requests
import datetime # pour verifier le temps, et calculer duree de session
import array # pour faire les listes
import socket #socket module pour recuperer IP
#import speedtest #pip install --user pyspeedtest #https://pyshark.com/test-internet-speed-using-python/
import inspect # for speedtest aussi 
import subprocess # pour changer hostname in linux
import os # pour verifer os et creer une dossier
import platform # pour verifer version d'os
from pathlib import Path # pour creer une dossier s'il n'existe pas
import csv


#calcul de temps de session
timeStart = datetime.datetime.now().replace(microsecond=0) 

    #nombre de folllowers et données sous forme 3,782 18.2k 20k 20.5m
    #ce qui n'est pas directement convertible a entier
    #on doit utiliser cette fonction pour passer à entiers
def convert_number(number):

    try:
        number = str(number) #pour debugger # ça doit convertir 2 fois pour bugger
        number = (number.replace(',',''))

        number = (number.replace('.1k','100'))
        number = (number.replace('.2k','200'))
        number = (number.replace('.3k','300'))
        number = (number.replace('.4k','400'))
        number = (number.replace('.5k','500'))
        number = (number.replace('.6k','600'))
        number = (number.replace('.7k','700'))
        number = (number.replace('.8k','800'))
        number = (number.replace('.9k','900'))

        number = (number.replace('k','000'))

        number = (number.replace('.1m','100000'))
        number = (number.replace('.2m','200000'))
        number = (number.replace('.3m','300000'))
        number = (number.replace('.4m','400000'))
        number = (number.replace('.5m','500000'))
        number = (number.replace('.6m','600000'))
        number = (number.replace('.7m','700000'))
        number = (number.replace('.8m','800000'))
        number = (number.replace('.9m','900000'))

        number = (number.replace('m','000000'))

        return int(number)
    
    except:
        print(check_time(),"ERROR.Failed to convert number")
        return 0;

    #verifie la connetion internet
    #ne congele pas le programme il y en a pas
    #affiche aussi ping
def check_connection():
    
    url='http://www.instagram.com/'
    timeout=10
    
    try:
        start = datetime.datetime.now() # pour calculer ping
        request = requests.get(url, timeout=timeout)
        fin = datetime.datetime.now()
        ping = str(fin - start)[:-3] # supprime 3 dernieres chiffres
        ping = (ping.replace('0:00:','')) # pour cacher minutes et heures
        #ping=('%02d.%d'%(ping.second,ping.microsecond))[:-3]
        print(check_time(),"Connected to the Internet, Ping = ",ping)
        return True
    except requests.ConnectionError:
    #except (requests.ConnectionError, requests.Timeout) as exception:
        print(check_time(),"No internet connection.")
    return False


    #congele le programe s'il y a pas de connexion internet
    #verifie la connextion chaque 10 seconds
def check_internet():
    
    try:
        url='http://www.instagram.com/'
        timeout = 10
        internet = False

        #boucle quand il y a pas d'internet
        while(internet != True):    
            try:
                start = datetime.datetime.now()
                request = requests.get(url, timeout=timeout)
                fin = datetime.datetime.now()
                ping = str(fin - start)[:-3] # supprime 3 dernieres chiffres
                ping = (ping.replace('0:00:','')) # pour cacher minutes et heures
                #print(check_time(),"Connection is working.Ping =",ping)
                internet = True
                return True       
            except requests.ConnectionError:
            #except (requests.ConnectionError, requests.Timeout) as exception:
                print(check_time(),"No internet connection. Waiting 20 second to reconnect")
                sleep(20)
    except:
        print(check_time(),"ERROR.Failed to evaluate internet connection and its speed.")
    finally:
        if internet == True:
            ping = float(ping)
            #print(check_time(),"Connection is working.Ping =",ping)
            if ping < 0.5:
                print(check_time(),"Connection is very fast. ( ping =",ping,")")
            elif ping < 1:
                print(check_time(),"Connection is fast. ( ping =",ping,")")
            elif ping < 1.5:
                print(check_time(),"Connection is normal. ( ping =",ping,")")
            elif ping < 3:
                print(check_time(),"Connection is slow. ( ping =",ping,")")
            else:
                print(check_time(),"Connection is very slow. ( ping =",ping,")")



def check_os():
    try:
        print(check_time(),"Operating system:",platform.system(),platform.release())
        return platform.system()
    except:
        print(check_time(),"ERROR.Failed to get OS and platform name.")



    
    #verifie le temps actuel
def check_time():
    try:
        now = datetime.datetime.now()
        #hour = str(now.hour)
        #minute = str(now.minute)
        #second = str(now.second)
        #time_now = str('' + hour + ':' + minute + ':' + second + '')
        return datetime.datetime.now().replace(microsecond=0)
    except:
        print("ERROR.Uknown datetime.")
        return "UKNOWN DATETIME"

   
   #verifie l'adresse IP et nom de host 
#@staticmethod
def check_ip():
    try:
        hostname = socket.gethostname()
        ip_adress = socket.gethostbyname(hostname)
        print(check_time(),f"Hostname: {hostname}")
        print(check_time(),f"IP Adress: {ip_adress}")
    except:
        print(check_time(),"ERROR.Failed to get IP adress.")


    #verifie le temps d'un session
def time_session():
    try:
        #timeStart = datetime.datetime.now().replace(microsecond=0)
        timeStop = datetime.datetime.now().replace(microsecond=0)
        print(check_time(),"Session time",timeStop - timeStart)
        return timeStop - timeStart
    except:
        print(check_time(),"ERROR.Failed to get time of session.")

def get_time_session():
    return time_session()

def get_time_start():
    return timeStart

def get_time_finish():
    return datetime.datetime.now().replace(microsecond=0)


def long_sleep(h,m,s):
    
    #integrité des données
    if h > 24:
        h = 24
    if m > 60:
        m = 60
    if s > 60:
        s = 60
    
    print(check_time(),"Bot will sleep for",h,"hours",m,"minutes",s,"seconds")
    sleep_time = s + (m*60) + (h*3600)
    sleep(sleep_time)

def create_file(filepath):

    try:
        if not os.path.exists(filepath):
            with open(filepath,'a',newline = '') as file:
                writer = csv.writer(file)
                #writer.writerow(["nom_utilisateur","date_start","date_finish","time_session","nbr_posts_start","nbr_followers_start","nbr_followings_start","nbr_posts_end","nbr_followers_end","nbr_followings_end","nbr_followed","nbr_unfollowed","nbr_requests","nbr_liked","nbr_commented","error_follow","error_unfollow","error_like","error_comment","error_login"])
    except Exception as exception:
        traceback.print_exc()
        print(check_time(),"ERROR.File",filepath,"could not be created.")

#"/my/directory"
def makedirectory(directory):

    #verifie si le dossier existe
    try:
        if not os.path.exists(directory):
            print(check_time(),"Creating directory",directory)
    except:
        print(check_time(),"ERROR. Failed to check existence of folder.")
      
    #cree une dossier s'il n'existe pas  
    try:  
        Path(directory).mkdir(parents=True, exist_ok=True)
    except:
        print(check_time(),"ERROR.Failed to create directory.")
    
#cree une dossier qui va contenir les profiles
makedirectory('profiles')

#pour fonction write
def make_logs():

    try:
        #cree une directoire pour les logs et erreurs
        makedirectory('logs')
        #makedirectory('logs/errors')
        file = 'logs/' + str(timeStart).replace(':',' ') # il faut remplacer pour eviter OS error
        #file = errors.txt
        create_file(file)
        return 'logs/' + str(timeStart)
    except Exception as exception:
        traceback.print_exc()

#logfile = make_logs() 


def write(text,file):

    print(text)

    try:
        if not os.path.exists(file):
            with open(file,'a',newline = '') as file:
                writer = csv.writer(file)
                writer.writerow([text])
    except Exception as exception:
        traceback.print_exc()
        print(check_time(),"ERROR.File",file,"could not be created.")    






#writer.writerow([follows_name, date_follow, nbr_posts,nbr_followers,nbr_followings,private])
#create csv 
def create_followscsv(csvpath):
    try:
        if not os.path.exists(csvpath):
            #file = open(csvpath, "w")
            #file.writerow(["name","date follow","number of posts","number of followers","number of follows","private"])
            with open(csvpath,'a',newline = '') as file:
                writer = csv.writer(file)
                writer.writerow(["name","date follow","number of posts","number of followers","number of follows","private","followbacker","followed from"])
    except Exception as exception:
        traceback.print_exc()
        print(check_time(),"ERROR.File",csvpath,"could not be created.")


def create_sessioncsv(csvpath):

    try:
        if not os.path.exists(csvpath):
            #file = open(csvpath, "w")
            #file.writerow(["name","date follow","number of posts","number of followers","number of follows","private"])
            with open(csvpath,'a',newline = '') as file:
                writer = csv.writer(file)
                writer.writerow(["nom_utilisateur","date_start","date_finish","time_session","nbr_posts_start","nbr_followers_start","nbr_followings_start","nbr_posts_end","nbr_followers_end","nbr_followings_end","nbr_followed","nbr_unfollowed","nbr_requests","nbr_liked","nbr_commented","error_follow","error_unfollow","error_like","error_comment","error_login"])
    except Exception as exception:
        traceback.print_exc()
        print(check_time(),"ERROR.File",csvpath,"could not be created.")



#c'est n'est pas utilisé
def str_to_hour(hour_str):
    
    try:
        hour_str = str(hour_str)
        date_time_obj = datetime.datetime.strptime(hour_str, '%H:%M:%S')
        return date_time_obj
    except Exception as exception:
        traceback.print_exc()

def str_to_date(date_time_str):
    try:
        date_time_str = str(date_time_str)
        date_time_obj = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S') 
        return date_time_obj
    except Exception as exception:
        traceback.print_exc()

def convert_to_seconds(hour,minute = 0,second = 0):
    
    return hour*3600 + minute*60 + second
    

