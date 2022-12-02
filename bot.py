from selenium import webdriver #pip install selenium
from time import sleep 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException # importe les exceptions
from selenium.webdriver.chrome.options import Options
from fonc import * # import tout le fonctions
from const import *
import requests # package pour verifier la connection internet # pip instal requests
import datetime # pour verifier le temps, et calculer duree de session
import array # pour faire les listes
import socket #socket module pour recuperer IP
import inspect # for speedtest aussi 
import subprocess
import random # pour generer nombres aleatoires
import traceback #pour montrer les erreurs
import sys #pour montrer les erreurs
#import pyautogui
import csv #sert a manipuler le fichier follows.csv
import numpy as np
import pandas as pd
import datetime
import logging
import threading 
import os


#variable pour linux pour que crontab ne bug pas
os.environ['DISPLAY'] = ':0'


######-------        PASS        -------######

default_username = 'x'
default_password = 'x'

#--------------------------------------------#

#variables deviennent True si compte est restrain d'abonner plus et ça empechera d'essayer d'abonner
restricted_follow = False
restricted_unfollow = False
restricted_like = False
restricted_comments = False



    #écris une commentaire
def typephrase(comment, field): 

    for letter in comment: # commentary and lyrics    
        field.send_keys(letter) # type the letter in the field
        sleep(0.09) # input time of each letter
        

    #lis la liste des amis et la retourne
def read_friends(file = 'do_not_unfollow.txt'):

    try:
        with open(file) as f:
            do_not_unfollow = [line.rstrip() for line in f]    
            
        f.close()
        return do_not_unfollow
        
    except FileNotFoundError:
        print(check_time(),'ERROR.File(',file,') was not found.')        
        return False

#lis les amis dans le fichier
do_not_unfollow = read_friends()    

    #lis liste les commentaires
def read_comments(file = 'comments.txt'):
    try:
        with open(file) as f:
            comments = [line.rstrip() for line in f]    
            
        f.close()
        return comments
        
    except FileNotFoundError:
        print(check_time(),'ERROR.File(',file,') was not found.')        
        return False

#lis les commentaires dans le fichier
comments = read_comments()

#lis les profiles a abonner
def read_profiles_follow(file = 'profiles_to_follow.txt'):
    try:
        with open(file) as f:
            profiles_to_follow = [line.rstrip() for line in f]    
            
        f.close()
        return profiles_to_follow
        
    except FileNotFoundError:
        print(check_time(),'ERROR.File(',file,') was not found.')        
        return False


profiles_to_follow = read_profiles_follow()

#génére un profil aleatoire a partir de laquelle on peut abonner
def random_profile():  

    try:
        global profiles_to_follow
        profile = random.choice(profiles_to_follow)
        profiles_to_follow.remove(profile)
        return profile
    except IndexError:
        print("ERROR")
        return random.choice(read_profiles_follow())


    #genere un commentaire aleatoire
    #supprime ce commentaire de la liste (pour eviter de publier 2 fois la meme chose)
    #s'il y a pas assez de commentaires dans la liste lis la liste et genere une automatiquement
def random_comment():  

    try:
        global comments
        com = random.choice(comments)
        comments.remove(com)
        return com
    except IndexError:
        return random.choice(read_comments())


class InstaBot:
    
    def __init__(self,username = default_username,password = default_password,disable_images = True):       
        self.__username = username
        self.__password = password
        self.__disable_images = disable_images
        
        #au cas où on utilise pas les données par dafaut
        self.set_username(username)
        self.set_password(password)
          
        #pour calculer nombre total d'utilisaterus abonné et désabonnées
        self.total_followed = 0 
        self.total_unfollowed = 0  
        self.total_like = 0 
        self.total_comment = 0   
        self.total_requests = -1 # nombre de follow requests
        
        #creation de repertoire pour informations sur les utilisteurs qu'on abonné
        self.path_follows = 'profiles/' + self.get_username() + '/' + 'follows.csv'
        self.path_session_info = 'profiles/' + self.get_username() + '/' + 'session_info.csv'
        self.path_all_sessions_info = 'profiles/' + 'all_sessions_info.csv'
        
        #stats initial et final ( nombre de posts, followers, followings )
        self.stats_start = []
        self.start_end = []
        
        print("====================================================================")
        print(check_time(),"Instagram bot has started.")

        check_os()
        check_internet()
        check_ip()
            
        #initialise le driver pour le bot    
        self.initialise_chromedriver()
        
        #si la page instagram ne peut pas etre ouvert Ã§a finit le programme
        if (self.goto_web("https://www.instagram.com") == False):
            self.bot_exit()        
            sys.exit()
            
        try:
            #click sur Accept bouton pour continuer
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Accept']"))).click() 
            print(check_time(),"Instagram page is open.")

            #log in to instagram account
            self.log_in()
                    
            #va sur la page de profil      
            self.goto_web("https://www.instagram.com/" + self.get_username()) 
            sleep(5)
            
        except:
            print(check_time(),"ERROR.Failed to log in to your profile.")
            self.bot_exit()              
            
        #essaie de cliquer log in alors que c'est impossible à faire en cas de connexion correcte
        try:
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//*[text()='Log In']"))).click()        
            print(check_time(),"ERROR.Failed to log in to your profile.")
            self.bot_exit() 
            self.failed_loggin = True
        except: #bot continue fonctionnement correctement
            print(check_time(),"Successfully logged in.")   
            self.failed_loggin = False
        
        if self.failed_loggin == True:
            sys.exit() #finis le programme
           
        try:
            print(check_time(),"Your account name:",self.get_username())
            self.stats_start = self.get_your_account_stats() #verifie nombre de posts,followers etc
            makedirectory('profiles/' + self.get_username())
            create_followscsv(self.get_path_follows())
            create_sessioncsv(self.path_session_info)
            self.read_follows_date()
            print(check_time(),"Bot followed",self.get_number_followed_users(),"users in total.")
            print("====================================================================")
        except:
            print(check_time(),"ERROR.Failed to create csv file")
            self.bot_exit()        



    def get_path_follows(self):
        return self.path_follows
        
    def set_path_follows(self,newpath):
        self.path_follows = newpath
    
    def get_password(self):
        return self.__password  
    
    def get_username(self):
        return self.__username

    def set_password(self,new_password):
        self.__password = new_password

    def set_username(self,new_username):
        self.__username = new_username

    #ajoute les informations par rapport à utilisateur abonné dans follow.csv
    def add_record_followscsv(self,follows_name,nbr_posts,nbr_followers,nbr_followings,private,followed_from):
    
        self.get_path_follows()
        date_follow = check_time()
        followbacker = False

        try:
            with open(self.get_path_follows(),'a',newline = '') as file:
                writer = csv.writer(file)
                writer.writerow([follows_name, date_follow, nbr_posts,nbr_followers,nbr_followings,private,followbacker,followed_from])
            file.close() # je sais pas si c'est necassaire 
        except:
            print(check_time(),"ERROR.Failed to write data to csv file.")

    
    #concerne session_info.csv (à la fin de session)
    def add_record_sessioncsv(self):
              
        global restricted_follow
        global restricted_unfollow
        global restricted_like
        global restricted_comments 
        
        nom_utilisateur = self.get_username() # nom de compte sur lequel bot est connecté
        date_start = get_time_start() #debut de session
        date_finish = get_time_finish() # fin de session
        time_session = get_time_session() # calcul de temps de session
        nbr_followed = self.total_followed # nombre d'utilisateurs abonnées
        nbr_unfollowed = self.total_unfollowed # nombre d'utilisateurs desabonnes
        nbr_requests =  self.total_requests # nombre de follow request supprimés
        nbr_liked = self.total_like # nombre de posts likés
        nbr_commented = self.total_comment # nombre posts commentés
        error_follow = restricted_follow # verifie si le compte est restraint d'abonner
        error_unfollow = restricted_unfollow # verifie si le compte est restraint de desabonner
        error_like = restricted_like # verifie si compte est restraint de liker
        error_comment = restricted_comments #verifie si compte est restraint de commenter
        error_login = self.failed_loggin # verifie si login est reussi

        nbr_posts_start = self.stats_start[0]
        nbr_followers_start = self.stats_start[1]
        nbr_followings_start = self.stats_start[2]
        
        nbr_posts_end = self.stats_end[0]
        nbr_followers_end = self.stats_end[1]
        nbr_followings_end = self.stats_end[2]
        
        
        if self.failed_loggin == False:
        
            try:
                with open(self.path_session_info,'a',newline = '') as file:
                    writer = csv.writer(file)
                    writer.writerow([nom_utilisateur, date_start, date_finish,time_session,nbr_posts_start,nbr_followers_start,nbr_followings_start,nbr_posts_end,nbr_followers_end,nbr_followings_end,nbr_followed,nbr_unfollowed,nbr_requests,nbr_liked,nbr_commented,error_follow,error_unfollow,error_like,error_comment,error_login])
                file.close() # je sais pas si c'est necassaire 
            except:
                print(check_time(),"ERROR.Failed to write data to csv file.")


    #lis follows.csv et retourne juste une liste des utilisateurs abonnées avec ce bot
    def read_follows_list(self):
    
        try:         
            df = pd.read_csv(self.get_path_follows(), sep =',')
            #for i, row in df.iterrows():
                #print(row)
     
            #ligne
            #columns = list(df) 
            #for i in columns: 
                #print (df[i][0]) 
                
            follows = []
            #colonne 
            for i, row in df.iterrows():
                name = row['name']
                #print(name)
                follows.append(name)
                #date_follow = row['date follow']
                #print(date_follow)

            #print(follows)
            return follows

        except Exception as exception:
            traceback.print_exc()
        

    #retourne nombre d'utilisateurs abonné avec ce bot
    def get_number_followed_users(self):
        try:
            df = pd.read_csv(self.get_path_follows(), sep =',')
            return df.shape[0]
        except:
            print(check_time(),"ERROR.Could not load number of followed users.")
            return 0
            
    #ça lis les utilisateur de follows.csv et calcule le temps qui a passé depuis leur abonnement
    #si asset de temps est passé on l'ajoute sur le liste pour le desabonner
    def read_follows_date(self):
        
        try:     
            df = pd.read_csv(self.get_path_follows(), sep =',')
            #for i, row in df.iterrows():
                #print(row)
            
            #ligne
            #columns = list(df) 
            #for i in columns: 
                #print (df[i][0]) 
            
            follows = []
            #colonne 
            for i, row in df.iterrows():
                name = row['name']
                #print(name)
                #follows.append(name)
                date_follow = row['date follow']
                date_follow = str_to_date(date_follow)
                #print(date_follow)
                time_follow =  check_time() - (date_follow)
                #print(time_follow)
                if time_follow.total_seconds() < convert_to_seconds(unfollow_after):
                    follows.append(name)

            #print(follows)
            return follows

        except Exception as exception:
            traceback.print_exc()


    def initialise_chromedriver(self):
        try:

            #ouvre chrome en anglais pour empecher les bugs
            options_lang = webdriver.ChromeOptions()            
            prefs_langue = {'intl.accept_languages': 'en,en_US'} #english
            
            #dans le cas ou on a choisi l'option dans le contructeur
            #bloque téléchargement des images
            if self.__disable_images == True:         
                prefs_images = {"profile.managed_default_content_settings.images": 2} #disable photos
                prefs_langue.update(prefs_images)
            
            options_lang.add_experimental_option("prefs", prefs_langue)
            #options_lang.add_argument('--headless')
            #options_lang.add_argument("--disable-gpu") 
            
            self.driver = webdriver.Chrome(options=options_lang)
            print(check_time(),"Chromedriver is running.")
        
        except Exception as exception:
            traceback.print_exc()    
            print(check_time(),"ERROR.Failed to open chromedriver. Chromedriver version may be obsolete.")
            self.bot_exit()
            
            
    #verifie ton nombre de posts,followers etc.
    def get_your_account_stats(self):
    
        try: #verifie nombre de posts
            number_posts = self.check_posts()
            print(check_time(),"You published:",number_posts,"posts.")

        except:
            print(check_time(),"ERROR.Could not load number of posts.")

        try: #verifie nombre de followers 
            number_followers = self.check_nbr_followers()
            print(check_time(),"You have:",number_followers,"followers.")

        except:
            print(check_time(),"ERROR.Could not load number of followers.")

        try: #verifie nombre d'utilisateurs que tu suis
            number_followings = self.check_followings()
            print(check_time(),"You follow:",number_followings,"users")
        except:
            print(check_time(),"ERROR.Could not load number of users you follow.")
        
        return number_posts,number_followers,number_followings
           
         


    #verifie nombre de posts
    def check_posts(self):
        try: 
            number_posts = self.driver.find_element_by_xpath('/html/body/div[1]/section/main/div/header/section/ul/li[1]/span/span').text
            number_posts = convert_number(number_posts)
            return number_posts
        except:
            number_posts = -1
            print(check_time(),"ERROR.Could not load number of posts.")
            return number_posts        


    #verifie nombre de followers 
    def check_nbr_followers(self):
        try: 
            number_followers = self.driver.find_element_by_xpath('/html/body/div[1]/section/main/div/header/section/ul/li[2]/a/span').text
        except:
            #en cas de compte prive
            try: 
                number_followers = self.driver.find_element_by_xpath('/html/body/div[1]/section/main/div/header/section/ul/li[2]/span/span').text
            except:
                number_followers = -1
                print(check_time(),"ERROR.Could not load number of followers.")   
        finally:
            return convert_number(number_followers)


    #verifie nombre d'utilisateurs que tu suis
    def check_followings(self):
        try: 
            number_followings = self.driver.find_element_by_xpath('/html/body/div[1]/section/main/div/header/section/ul/li[3]/a/span').text            
        except:
            #en cas de compte prive
            try: 
                number_followings = self.driver.find_element_by_xpath('/html/body/div[1]/section/main/div/header/section/ul/li[3]/span/span').text
            except:
                number_followings = -1
                print(check_time(),"ERROR.Could not load number of followings.")
        finally:
            return convert_number(number_followings)


    #verifie si le profil d'utilisateur est privÃ© ou pas
    def isPrivate(self):
        try:    #test consiste a verifie nombre de followings number_followings
            test = self.driver.find_element_by_xpath('/html/body/div[1]/section/main/div/header/section/ul/li[3]/span/span').text
            return True
        except:
            return False


    #verifie si utilisateur qu'on veut abonner repondre aux criteres dans le fichier const
    #si oui retourne True
    def check_follower(self,user = 'User'):
 
        number_posts = self.check_posts()
        number_followers = self.check_nbr_followers()
        number_followings = self.check_followings()    

        if ignore_private == True:
            if self.isPrivate() == True:
                print(check_time(),user,"has private account.Cannot follow private accounts.")
                return False
        
        if compare_posts == True:
            if number_posts > max_posts:
                print(check_time(),user,"published more posts than",max_posts)    
                return False
            if number_posts < min_posts or number_posts == -1:
                print(check_time(),user,"published less posts than",min_posts)
                return False
        
        if compare_followers == True:
            if number_followers > max_followers:
                print(check_time(),user,"has more followers than",max_followers)
                return False
            if number_followers < min_followers or number_followers == -1:
                print(check_time(),user,"has less followers than",min_followers)
                return False 
        
        if compare_followings == True:
            if number_followings > max_followings:
                print(check_time(),user,"follows more users than",max_followings)
                return False
            if number_followings < min_followings or number_followings == -1:
                print(check_time(),user,"follows less users than",min_followings)
                return False 
                      
        return True


    def goto_web(self,website):
    
        #verifie si on ouvre pas le site web oÃ¹ on est dÃ©ja
        if (self.check_url() != (website)):
            try:
                self.driver.get(website)
                return True
            except:
                print(check_time(),"ERROR.Failed connection to",website)
                try:
                    check_internet()               
                    print(check_time(),"Retrying connection to",website)
                    self.driver.get(website)
                except:
                    print(check_time(),"ERROR.Failed again to reconnect")
                    return False
        #si on est sur bon website         
        elif (self.check_url() == (website)):
            print(check_time(),"You are already on the website.")
            return True


    def open_followings_list(self):
    
        try:
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/section/main/div/header/section/ul/li[3]/a'))).click()
        except:
            print(check_time(),"ERROR. List could not be loaded with xpath.")
            check_internet()
            self.driver.refresh()
            sleep(10)
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/section/main/div/header/section/ul/li[3]/a'))).click()
        finally:
            sleep(30)


    def scroll_to_bottom(self,nbr_users):
    
        errCount = 0
        
        for x in range(1, nbr_users + 1):

            nbr = str(x) # converti int en string
               
            if(x%5==0): # scrolle chaque 5 followers
                try:                   
                    if x <= 10:#usr = self.driver.find_element_by_xpath('/html/body/div[5]/div/div/div[2]/ul/div/li[' + nbr + ']/div/div[2]/div[1]/div/div/span/a')
                        usr = self.driver.find_element_by_xpath('/html/body/div[5]/div/div/div[2]/ul/div/li['+nbr+']')
                        self.driver.execute_script('arguments[0].scrollIntoView()', usr) #Ã§a scrolle
                    else:
                        usr = self.driver.find_element_by_xpath('/html/body/div[5]/div/div/div[2]/ul/div/li['+nbr+']/div')
                        self.driver.execute_script('arguments[0].scrollIntoView()', usr)
                        
                    print(check_time(),"Scrolled to position:",nbr,"/",nbr_users)               
                except:
                    try:
                        check_internet()
                        self.resize_window(904,1085) # test pour debugger si le fenetre est minimalisé
                        self.resize_window()
                        sleep(8)
                        self.driver.execute_script('arguments[0].scrollIntoView()', usr) #Ã§a scrolle
                        print(check_time(),"Scrolled to position:",nbr,"/",nbr_users)
                    except Exception as exception:
                        #traceback.print_exc() #cette traceback est trop aggressive 
                        print(check_time(),"ERROR. Failed to scroll the list.")
                        errCount = errCount + 1
                        print(check_time(),"ERROR. Failed to scroll.",errCount,"/5")
                        if errCount >= 5:
                            print(check_time(),"ERROR. Failed to scroll the list. Exiting the list...")
                            return False
                finally:
                    sleep(2)
                    
        return True
   
       
    
    #ajoute les utilisateurs scannÃ©es a la liste
    def create_list(self,nbr_users):

        #cree une liste de followings    
        users = [] 
        
        #boucle pour ajouter les utulisateurs qu'on a abonnÃ© sur la liste
        for y in range(1,nbr_users+1):
            nbr = str(y) # converti int en string

            try:                
                username_path = '/html/body/div[5]/div/div/div[2]/ul/div/li['+ nbr +']/div/div[1]/div[2]/div[1]/span/a'
                user = self.driver.find_element_by_xpath(username_path).text
                users.append(user)
            except:
                print(check_time(),"ERROR.User is not found.")
                
        return users  


    #basÃ© sur scroll_to_bottom et create_list
    #generer une base des 
    #si la liste n'est pas gÃ©nÃ©rÃ© correctement Ã§a refait le scans
    #sert juste pour les followers
    #FONCTIONNE JUSTE POUR LES FOLLOWERS
    def gen_usr_list(self,nbr_users,usr_type = 'followings'):
        
            
        for x in range(4):
            if self.scroll_to_bottom(nbr_users) == True:
                users = self.create_list(nbr_users)
                return users
            else:
                print(check_time(),"ERROR. List of users is not loaded correctly.")
                #self.driver.refresh() #marche mais sert a rien ici
                try:
                    self.driver.refresh()
                    sleep(10)
                    if usr_type == 'followings':          
                        self.open_followings_list()
                    else:
                        self.open_followers_list()
                    sleep(20) # a modifier apres
                except:
                    print(check_time(),"ERROR. Could not reload website.")

        return False


    #regarde les stories aleatoires
    def watch_stories(self,minutes=2):
        try:
            self.goto_web("https://www.instagram.com")
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//*[text()='Not Now']"))).click()
            sleep(10)
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="react-root"]/section/main/section/div[1]/div[1]/div/div/div/div/ul/li[3]/div/button/div[2]'))).click()
        except:
            print(check_time(),"ERROR. Failed to watch stories")
        
        sleep(minutes*60)


    #on desabonne nbr_to_unfollow
    #scan_all_followings si vrai scanne tout la liste pour desabonner exectement nbr_to_unfollow
    #not_following_only si vrai desabonne uniquement ceux qui ne sont pas abonnée a nous
    def unfollow_users(self,nbr_to_unfollow,scan_all_followings=True,reverse_order=True,not_following_only=False):

        #verification si on peut desabonner
        global restricted_unfollow
        if restricted_unfollow == True:
            print(check_time(),"ERROR.Cannot unfollow because account is restricted.")
            return False  

        #pour calculer nombre d'utilisateurs desabonnes avec cette fonction
        number_unfollowed = 0

        time_start_function = datetime.datetime.now().replace(microsecond=0)

        print("------------------------------------------------------------")
        print(check_time(),nbr_to_unfollow,"users will be unfollowed.")

        check_internet()

        # pour empecher le bug
        if nbr_to_unfollow < 10:
            print(check_time(),"ERROR.Number of users to unfollow can not be less than 10.")
            return False
                
        try:   
            if self.goto_web('https://www.instagram.com/' + self.get_username() + '/') == True:
                sleep(15)                   
                number_followings = self.check_followings()
                if number_followings != -1 and number_followings < nbr_to_unfollow:
                    nbr_to_unfollow = number_followings
                    print(check_time(),"WARNING.Too many users to unfollow.Only",nbr_to_unfollow,"will be unfollowed.")
            else:
                return False

            #creation de liste de nos followers
            if not_following_only == True:
                number_followers = self.check_nbr_followers()
                #print(check_time(),"You have:",convert_number(number_followers),"followers.")
                self.open_followers_list()
                print(check_time(),"Your followers are scrolled.")
                
                followers = self.gen_usr_list(number_followers,"followers")
                if followers == False:
                    return False

                #arrete la fonction s'il y a une erreur dans la liste
                if len(followers) + 20 < number_followers: #number_followers:
                    print(check_time(),"ERROR. Liste of followers is not complete.")
                    return False        

                print("List of followers:")        
                print(followers)

            #ici il y a 2eme partie du code pour desabonner        
            
            #ouvre notre profil d'instagram
            self.goto_web("https://www.instagram.com/" + self.get_username())   

            self.open_followings_list()
            
            print(check_time(),"Users are scrolled to be unfollowed.")
            
            if scan_all_followings == True:
                followings = self.gen_usr_list(number_followings,"followings")
            else: #alors on va scanner juste une partie
                followings = self.gen_usr_list(nbr_to_unfollow,"followings")                
            
            if followings == False:
                return False            
            
            #verifie si nombre d'abonnement est correcte
            if len(followings) < 2:
                return False
            
            if reverse_order == False:
                print("List of followings:")        
                print(followings)          
                
            if reverse_order == True:
                followings.reverse()
                print("Reversed list of followings:")
                print(followings)

            print(check_time(),nbr_to_unfollow,"users will be unfollowed.")

            #verifie si on a tout scanné ou pas
            if scan_all_followings == True or reverse_order == True:
                repetitions = len(followings)
            else:
                repetitions = nbr_to_unfollow

            #boucle pour desabonner
            for x in range(0,repetitions):

                try:               
                    isSame = False #pour comparer les chaines de caractere
                                   #il faut le mettre Ã  False sinon Ã§a desabonnera personne

                    #verifie si c'est un ami
                    for y in range(0,len(do_not_unfollow)): #do_not_unfollow
                        try:
                            if unfollow_friends == True and followings[x] == do_not_unfollow[y]:
                                isSame = True
                                print(check_time(),followings[x],"is your friend and he will not be unfollowed.")
                        except:
                            break #pour empecher index out of range
                            
                            
                    #si on a choisi option "desabonner uniquement utilisateur ne pas abonnées"   
                    if not_following_only == True: 
                        for y in range(0,len(followers)): 
                            if followings[x] == followers[y]:
                                isSame = True
                                print(check_time(),followings[x],"is following you and will not be unfollowed.")
                        
                    #si c'est pas ton ami ou follower ça continnue
                    if isSame == False: 
                        #Desabonnement
                        if self.unfollow(followings[x]) == True:
                            number_unfollowed = number_unfollowed + 1
                    
                    #test pour empecher d'abonner trop
                    if number_unfollowed >= nbr_to_unfollow:
                        return True
                
                except IndexError as exception:
                    traceback.print_exc()
                
                
        except Exception as exception:
            traceback.print_exc()
        finally:
            try:
                time_stop_function = datetime.datetime.now().replace(microsecond=0)
                print(check_time(),number_unfollowed,"users has been unfollowed during",time_stop_function - time_start_function)
            except:
                print(check_time(),"ERROR. Failed to check time interval") 


    #desabonner un utilisateur
    def unfollow(self,user):
           
        #global total_unfollowed
        global restricted_unfollow
        
        follows = self.read_follows_date()
        
        #verifie si utilisateur est dans la liste (pour ne pas desabonner trop tot)
        for y in range(0,len(follows)):
            if user == follows[y]:
                print(check_time(),"It is too early to unfollow",user)
                return False               
   
        #pour ne pas desabonner si compte est restraint
        if restricted_unfollow == True:
            return False
        
        #accede a la page
        if self.goto_web('https://www.instagram.com/' + user +'/') == False:
            return False
        
        #temps entre chaque desabonnement
        sleep(5 + delay_unfollow)

        #ouvre la fenetre avec confirmation de desabonnement       
        try:                                                                                             
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/div/div[2]/div/span/span[1]/button"))).click()
        except:
            try: #option pour supprimer les demandes d'abonnements
                WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Requested']"))).click()
            except:
                print(check_time(),"ERROR.Window to open unfollow request cannot be found.")
                return False       
        
        #clique sur le bouton unfollow
        try:                  
            sleep(5)
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Unfollow']"))).click()
            print(check_time(),user,"is unfollowed.") #information dans la console qui a Ã©tÃ© desabonnÃ©           
        except:
            print(check_time(),"ERROR.Unfollow button is not found.")
            print(check_time(),"ERROR.",user,"is not unfollowed.")
            return False

        #verifie si compte est restraint
        #si c'est le cas il arrete d'abonner             
        try:                                                                #'OK' ou 'Report a Problem'
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//*[text()='OK']"))).click()
            print(check_time(),"ERROR.Your account was temporally restricted from following.")
            restricted_unfollow = True
            return False
        except:
            #Ã§a veut dire que le compte n'est pas restraint
            self.total_unfollowed = self.total_unfollowed + 1
            return True        


    # supprime les demandes d'abonnement
    def delete_requests(self,nbr_req_remove):
    
        number_deleted_requests = 0
    
        if nbr_req_remove < 1:
            print(check_time(),"ERROR. Number of requests to remove cannot be less than 1.")
            return False
            
        try:
            #nombre de request supprimÃ©s
            #pour calculer combien de temps Ã§a a pris
            time_start_function = datetime.datetime.now().replace(microsecond=0)
            print("------------------------------------------------------------")
            print(check_time(),nbr_req_remove,"of requests will be removed.")
            check_internet()
            
            #va sur le site oÃ¹ sont les requests
            if self.goto_web("https://www.instagram.com/accounts/access_tool/current_follow_requests") == True:
                sleep(30)

            requests = [] #cree une liste des requests

            #boucle pour lire les requests
            nbrReq = 1000 #nombre maximale requests a lire
            for x in range(1,nbrReq+1):
                try:
                    nbr = str(x)
                    req = self.driver.find_element_by_xpath('/html/body/div[1]/section/main/div/article/main/section/div['+nbr+']').text
                    requests.append(req) #ajoute request a la liste
                    if(x%4 == 0):
                        if self.click_view_more() == True:
                            nbrReq = nbrReq + 4
                except:
                    print(check_time(),"End of request list.")
                    break

            print(check_time(),"Number of requests:",requests)
            print(len(requests))
            self.total_requests = len(requests) #recupere nombre de requests

            if len(requests) < 1:
                print(check_time(),"ERROR.Request list is empty.")
                return False

            #boucle pour ouvre compte d'utilisateur qui ont veut desabonner(supprimer request)
            for x in range(0,len(requests)):           
                try:
                    if self.unfollow(requests[x]) == True:
                        number_deleted_requests = number_deleted_requests + 1
                        if number_deleted_requests >= nbr_req_remove:
                            break
                except:
                    print(check_time(),"Error during removing request.")

        except Exception as exception:
            traceback.print_exc()
        finally:
            try:
                time_stop_function = datetime.datetime.now().replace(microsecond=0)
                print(check_time(),number_deleted_requests,"users has been unfollowed during",time_stop_function - time_start_function)
            except:
                print(check_time(),"ERROR. Failed to check time interval") 


    #abonne nombre indiquÃ© de followers(nbrFollowers) d'un utilisateur(user)
    #si like_photo est vrai like le premier photo
    def follow_from(self,nbrFollowers,user,like_post=False,comment_post=False):
    
        global restricted_follow
        if restricted_follow == True:
            return False  
    
        try:            
            if nbrFollowers < 10:
                print(check_time(),"ERROR.Number of users to follow can not be less than 10.")
                return False

            #nobre d'utilisateurs abonnÃ©es avec cette fonction cette fois
            number_followed = 0
                       
            #pour calculer combien de temps Ã§a a pris
            time_start_function = datetime.datetime.now().replace(microsecond=0)
            
            print("------------------------------------------------------------")
            print(check_time(),nbrFollowers,"users will be followed from",user)

            #verifie la connexion internet
            check_internet()
            
            #ouvre le profil instagram d'utilisateur
            self.goto_web("https://www.instagram.com/" + user)
            sleep(5)

            #ouvre la liste de followers
            self.open_followers_list()

            print(check_time(),"Followers of user",user,"are scrolled")

            followers = self.gen_usr_list(nbrFollowers,"followers")
            if followers == False:
                return False
            
            print("List of followers:")        
            print(followers)           
            
            #boucle pour abonner
            for x in range(0,len(followers)):

                if (self.follow(followers[x],like_post,comment_post,user)) ==  True: 
                    number_followed = number_followed + 1
                                               
        except Exception as exception:
            traceback.print_exc()
        finally:
            try:
                time_stop_function = datetime.datetime.now().replace(microsecond=0)
                print(check_time(),number_followed,"users has been unfollowed during",time_stop_function - time_start_function)
            except:
                print(check_time(),"ERROR. Failed to check time interval") 

    def follow(self,user,like=False,comment=False,followed_from = "UNKOWN"):
        
        global restricted_follow
        
        if restricted_follow == True:
            return False

        follows = self.read_follows_list()

        for y in range(0,len(follows)):
            if user == follows[y]:
                print(check_time(),user,"has been followed before. Cannot follow twice.")
                return False

        #verifie si on est sur la page de cet utilisateur
        #sinon on ouvre sa page
        
        self.goto_web('https://www.instagram.com/' + user +'/')
            
        sleep(10)#verifie nombre de posts, followers etc.     
        if (self.check_follower(user) == False):
            print(check_time(),user,"does not meet creteria to be followed.")
            return False
       
        try:    #click sur le bouton abonner                                                                         
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//*[text()='Follow']"))).click()
            print(check_time(),user,"was succesfuly followed.")
            sleep(5 + delay_follow) #temps entre chaque abonnement
        except:
            print(check_time(),"ERROR.",user,"has not been followed.")
            return False 

        #verifie si compte est restraint
        #si c'est le cas il faut arreter d'abonner              
        try:                                                                #'OK' ou 'Report a Problem'
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//*[text()='OK']"))).click()
            print(check_time(),"ERROR.Your account was temporally restricted from following.")
            restricted_follow = True
            return False
        except:
            #ça veut dire que le compte n'est pas restraint
            self.total_followed = self.total_followed + 1
            self.add_record_followscsv(user,self.check_posts(),self.check_nbr_followers(),self.check_followings(),self.isPrivate(),followed_from)

        #empeche de liker et mettre des commentaires si compte et privé
        if self.isPrivate() == True:
            print(check_time(),user,"has private account.")
            return True

        if like == True:
            self.like_post(user)
        
        if comment == True:
            self.comment_post(user)
            
        return True


    def like_post(self,user):
          
        global restricted_like
          
        #pour empecher le bugs
        self.goto_web("https://www.instagram.com/" + self.get_username())
        sleep(2)
        self.goto_web('https://www.instagram.com/' + user +'/')
        sleep(5)
        
        # quand utilisateur n'a pas publié les photos
        if self.check_posts() < 1:
            print(check_time(),user,"has no posts to like")
            return False
        
        try:
            #click sur la premiere photo et l'ouvre la fenetre oÃ¹ on peut clicker like par la suite
            self.driver.find_element_by_class_name("kIKUG").click()
            sleep(10)
            #click sur le like
            self.driver.find_element_by_class_name('fr66n').click()          
        except:
            print(check_time(),"ERROR. Photo of",user,"was not liked")

            #verifie si le compte est restraint de publiquer les commentaires
        try:
            sleep(3)
            self.driver.find_element_by_xpath('//button[contains(text(), "Retry")]').click()
            print(check_time(),"ERROR. Account is restricted. Comment cannot be published.")
            restricted_like = True
            return False
        except:
            self.total_like = self.total_like + 1
            print(check_time(),"Photo of",user,"was liked")




    #met un commentaire aleatoire des fichier comments.txt
    def comment_post(self,user):
    
        #global total_comment
        global restricted_comments
        
        if restricted_comments == True:
            return False
    
        self.refresh_page()
        self.goto_web('https://www.instagram.com/' + user +'/')
        
        #ouvre la fenetre avec la 1er photo
        try:
            sleep(10)        
            self.driver.find_element_by_class_name('v1Nh3').click()
        except:
            print(check_time(),"ERROR. Failed to open window with photo.")
            return False

        #click la oÃ¹ on met les commentaires
        try:
            sleep(10)
            self.driver.find_element_by_class_name('Ypffh').click() # click the field to insert comment
        except:
            print(check_time(),"ERROR. Failed to click the field to insert comment.")
            return False
        
        #clear field
        try:
            sleep(5)
            field = self.driver.find_element_by_class_name('Ypffh')
            field.clear()
        except:
            print(check_time(),"ERROR. Failed to clear field.")
            return False
        
        #ecrit une commentaire aleatoire et le publie
        try:
            comment = random_comment()
            typephrase(comment, field)
            sleep(5)
            self.driver.find_element_by_xpath('//button[contains(text(), "Post")]').click()
        except:
            print(check_time(),"ERROR. Failed to post comment.")
            return False
            
        #verifie si le compte est restraint de publiquer les commentaires
        try:
            sleep(3)
            self.driver.find_element_by_xpath('//button[contains(text(), "Retry")]').click()
            print(check_time(),"ERROR. Account is restricted. Comment cannot be published.")
            restricted_comments = True
            return False
        except:
            self.total_comment = self.total_comment + 1
            print(check_time(),"Comment:",comment,"was posted for",user)         
            

    def open_followers_list(self):
    
        try:
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/section/main/div/header/section/ul/li[2]/a'))).click()
        except:
            try:
                print(check_time(),"ERROR. List of followers could not be loaded.")
                check_internet()
                self.driver.refresh()
                sleep(10)       
                WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/section/main/div/header/section/ul/li[2]/a'))).click()
            except:
                print(check_time(),"ERROR. List of followers could not be loaded.")
        finally:
            sleep(30)    
            
    #affiche la somme d'utilisateurs abonnnÃ©s
    def print_total_follow(self):
    
        if self.total_followed !=0:
            print(check_time(),"Total of ",self.total_followed,"users have been followed.")
            return self.total_followed
        else:
            return False


    #affiche la sommme de posts commentÃ©s
    def print_total_comment(self):
    
        if self.total_comment !=0:       
            print(check_time(),"Total of ",self.total_comment,"posts have been commented.")
            return self.total_comment
        return False
     
     
    #affiche la somme de posts likÃ©
    def print_total_like(self):

        if self.total_like !=0:        
            print(check_time(),"Total of ",self.total_like,"posts have been liked.")
            return self.total_like
        else:
            return False
  

    #affiche la somme d'utilisateurs desabonnnÃ©s
    def print_total_unfollow(self):
        
        if self.total_unfollowed !=0:
            print(check_time(),"Total of ",self.total_unfollowed,"users have been unfollowed.")
            return self.total_unfollowed 
        else:
            return False


    #fonction cree pour delete_requests pour elargir la liste de requests
    def click_view_more(self):
        try:
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[text()='View More']"))).click()
            return True
        except:
            return False


    def resize_window(self,x=942,y=1087):
         self.driver.set_window_size(x,y)
         print(check_time(),"Window resized to",x,'px',y,'px')


    def get_window_size(self):
         size = self.driver.get_window_size()
         print("Window size: width = {}px, height = {}px.".format(size["width"], size["height"]))


    #click sur un element
    def clickElement(self,element):
        try:
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, element))).click()
            return True   
        except:
            print(check_time(),"ERROR.Element ",element,"not found.")
            return False

    
    def scroll(self,element):
        try:
            sleep(10)
            print(check_time(),"Scrolling to",element)
            usr = self.driver.find_element_by_xpath(element)
            self.driver.execute_script('arguments[0].scrollIntoView()', usr) #Ã§a scrolle
            return True
        except:
            print(check_time(),"ERROR.Scrolling to",element,"failed.")
            return False   
    
    
    def check_url(self):
        return self.driver.current_url
     
     
    def refresh_page(self):
        self.driver.refresh()
 
     
    #se connecter
    def log_in(self):
        try:
            for x in range (15):
                sleep(2)             
                if (self.check_url() == "https://www.instagram.com/"):
                    break
            self.driver.find_element_by_xpath("//input[@name=\"username\"]")\
                .send_keys(self.get_username())
            self.driver.find_element_by_xpath("//input[@name=\"password\"]")\
                .send_keys(self.get_password())
            self.driver.find_element_by_xpath("//input[@name=\"password\"]")\
                .send_keys(Keys.ENTER)                       
            #il faut attendre pour eviter les bugs
            sleep(8)  
            
        except:
            print(check_time(),"Failed to log in. Username or password can be incorrect.")                
            self.bot_exit()
             

    #se deconnecte
    def log_out(self):
        try:
            self.driver.get("https://instagram.com/accounts/logout/")
            sleep(2) # pour voir ce qui s'est passÃ©
            print(check_time(),self.get_username(),"is log out.")
            return True
        except:
            print(check_time(),"ERROR. Failed to log out.")
            return False


    #ferme le chromedriver
    def bot_exit(self):
        try:
            self.driver.quit() #ça finit le programme
            #self.driver.close() #ça ferme juste la fenetre
            print(check_time(),"Driver is closed.")
        except:
            print(check_time(),"ERROR.Failed to quit or close the driver.")
            

    #fin de session
    #log out, ferme nativateur et affiche nombre d'utilisateurs abonnes/desabonnes
    def end_session(self):
        print("====================================================================")    
        try:
            self.goto_web('https://www.instagram.com/' + self.get_username() + '/') 
            sleep(2)
            self.stats_end = self.get_your_account_stats()
        except:
            print(check_time(),"ERROR.Failed to load account statistics")
        try:
            self.add_record_sessioncsv()
            self.print_total_unfollow()
            self.print_total_follow()
            self.print_total_like()
            self.print_total_comment()
            self.log_out()
            self.bot_exit()
            print("====================================================================")
        except Exception as exception:
            traceback.print_exc()



