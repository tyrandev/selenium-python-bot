from bot import * # import tout le fonctions
import traceback
import sys
import logging
import threading


#profiles
#beautifuldogs #dog #dogs #dog_lovers_1 #insta_dog

def main():

    try:
        bot = InstaBot('xxxx','xxxx')
        bot.follow_from(10,'dog',True,True)
        bot.delete_requests(10)
        bot.unfollow_users(10)
        #bot.unfollow_all(100)
        #long_sleep(0,5,0)
        #bot.follow_from(60,'dog')
        #long_sleep(0,10,0)
        #bot.follow_from(50,'dogs')
        #long_sleep(0,15,0)
        #bot.follow_from(50,'insta_dog',True)
        
    #imprime l'erreur dans la console    
    except Exception as exception:
        traceback.print_exc()

    #se deconnecte et montre les statistiques
    finally:
        long_sleep(0,0,20)
        bot.end_session()


main()

#usefull pages
    
#comment liker les photos
# https://www.geeksforgeeks.org/like-instagram-pictures-using-selenium-python/

#projet interressant
#https://github.com/instabotai/instabotai

#AI pour reconnaitre les images
#https://machinelearningmastery.com/use-pre-trained-vgg-model-classify-objects-photographs/

#post a picture automatically in instagram
#https://www.geeksforgeeks.org/post-a-picture-automatically-on-instagram-using-python/
#https://medium.com/@selfengineeredd/how-to-post-on-instagram-using-python-fd8b08050a85


#minimize, maximise, resize browser
#https://sqa.stackexchange.com/questions/15484/how-to-minimize-the-browser-window-which-was-launched-via-selenium-webdriver
#https://stackoverflow.com/questions/3189430/how-to-maximize-the-browser-window-in-selenium-webdriver-selenium-2-using-c
#https://subscription.packtpub.com/book/web_development/9781849515740/2/ch02lvl1sec31/maximizing-the-browser-window
#https://www.guru99.com/maximize-resize-minimize-browser-selenium.html
