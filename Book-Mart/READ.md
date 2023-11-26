# BOOK-MART
#### Video presentation:  ***<https://youtu.be/_wYKkIX6R1s>***
### Description:  
this project basically a ecomerse website in which custemers can buy their usefull books and publishers can publish their books,
this idea strikes me when i saw some people in my locality are facing the issue that they can't able to sell in the multi national ecomerce websites like amazon or flipkart due to lack of tecnology .so i decided to gave a nice prodouct (app) which is free of cost and zero commision and a user friendly one so i stepped my first leg towords my wish.

## FILES 
  #### FOLDER :    ***BOOK-MART***
  ##### app.py - contins all the code required for the specifict  type of operations so basically it acts like a server where i did so many operations like :
          connecting to sqlite(database)
          connecting with html pages
      functions to gave the user preferable books
    to make the website dynamic :
        ex:1 preview for books 
        ex:2 passing imfo to web site (html)
      ex:3 using hash function to enhance security
        ex:4 to get user info from databases
  ##### ***helpers.py*** - which i adopted from cs50x pset 9 finance problem for sending apppology to user with its error code which make it more user friendly and can esily resolve the issue.
  ##### requirments.txt - it gave the list of python lib which i used for making the website and other resources i used for it 
  ##### bookmart.db  - have the following tables for data storage and processing
      1) Users
      2) Publisher
      3) Books
      4) History
  ### USER -> storing the data of coustumers
  ### PUBLISHER --> for the storage of publisher data set
  ### BOOKS -> which stores the list of BOOKS
  ### HISTORY -> which take care about cart system


# static :
  which contain one css file which styles the layout and apology  thats it . AND the remaining web pages have their own infile css styling

  ## favicon --> 
      which serves as icon for my entire web site
  ## index.jpg
      which serve as back-ground image for register.html
# Templates
### apology.html
    gave apology for every error or server issue
### cart.html
    take a list of books from server which gave the books imfo about books in cart for the active user
### categories.html
    tried to implement a page for grouping based upon their catogires but failed
### home.html
    which take all the formated books based up on the preference of user intrest then place on the web body using flex to become dynamic
    it conain links to cart and add to cart an d logout adn my portfolio
### layout.html
    which extended from pset such that to layout the apology letter
     and link to static css 
### login.html
    which was encorparated from bootstrap to look more eligent and dynamic for the user perspective
### preview.html
    it is the layout web which can gave the layout for each and every book by taking the value of the book which we want and use its conntendt  to format 
### publisher.html
    it is the home page of publisher in which they can add or delete their books they want based on the stock avaibility 
### register.html 
    where user or publisher going to login based up on which preference the user select there is immutable and the algorithm
    took over the data to format which is good for that persone
    and for users it took their email for contacting pourpose if the user needs their prodouct

~~~
      this documentation going to  help you took over the blue print of my web site such that you can able to understand the code better that's it.
~~~
    *** THANK YOU ***
