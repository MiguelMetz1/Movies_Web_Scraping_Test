# -*- coding: utf-8 -*-
"""main.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1obNiOnqN-S4PG9sVQe1jhcEh_3R2g3iS
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup

import random
from time import sleep

!pip install selenium
!apt-get update
!apt install chromium-chromedriver
!cp /usr/lib/chromium-browser/chromedriver /usr/bin

import sys
from selenium import webdriver

from selenium.webdriver.common.by import By

class Movie():

  def __init__(self, data:dict):
    """ Receives a dict with keys:
        [ "Title":str, "Year":numeric-str, "Synopsis":str, "Genres:str-list",
          "Link":str, "Comments":str-list, "Related Movies":str-list, 
          "Likes":str, "RTCritics %":str ,"RTAudience %":str ,"IMDb":str,
          "Directors":str-tuple, "Actors":str-tuple-tuple ]
    """

    self.__title = data.get("Title","")
    self.__year = data.get("Year","")
    
    self.__synopsis = data.get("Synopsis","")
    self.__link = data.get("Link","")
    self.__comments = data.get("Comments",[])
    self.__genres = data.get("Genres",[])
    
    self.__likes = data.get("Likes","")
    self.__RTCritics = data.get("RTCritics %","")
    self.__RTAudience = data.get("RTAudience %","")
    self.__IMDb = data.get("IMDb","")

    self.__relatedMovies = data.get("Related Movies",[])
    self.__directors = data.get("Directors",tuple())
    self.__actors = data.get("Actors",tuple())


  def getPrimaryData(self):
    """ Returns tuple with:
          title:str, year:str, synopsis:str, genres:str-list """
    return (self.__title, self.__year, self.__synopsis, tuple(self.__genres))


  def getSecondaryData(self):
    """ Returns tuple with:
          link:str, comments:str-list, relatedMovies:str-list """
    return (self.__link, tuple(self.__comments), tuple(self.__relatedMovies))

  
  def getRankingsData(self):
    """ Returns tuple with:
          likes:str, RottenTomatoesCritics:str, RottenTomatoesAudience:str, IMDb_Rating:str """
    return (self.__likes, self.__RTCritics, self.__RTAudience, self.__IMDb)


  def getCast(self):
    """ Returns tuple with:
          Directors:tuple, Actors:tuple """
    return (self.__directors, self.__actors)

#Prepare Selenium Driver
sys.path.insert(0,'/usr/lib/chromium-browser/chromedriver')
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
wd = webdriver.Chrome('chromedriver',chrome_options=chrome_options)


def getFirstComments(link:str):

  wd.get(link)

  comments_divs = wd.find_elements(By.CLASS_NAME,"comment")
  visibleComments = []

  print(f"--> Para la pelicula: '{link}'  hay {len(comments_divs)} comentarios.")

  for comment_div in comments_divs:
    
    p_tag = comment_div.find_element(By.TAG_NAME,"p")
    if not p_tag:
      continue

    p_tag.location_once_scrolled_into_view
    comment = p_tag.text
    if comment:
      visibleComments.append(comment)


  return visibleComments

def getMovieTitle( movieSoup ):
  """ Returns string with the title of the movie of the link """
  
  title = ""

  movieInfo = movieSoup.find("div", id="movie-info")

  if movieInfo:
    title_elem = movieInfo.find("h1")
    if title_elem:
      title = title_elem.text

  return title


def getMovieYear( movieSoup ):
  """ Returns the year(int) of the movie """

  year = ""

  movieInfo = movieSoup.find("div", id="movie-info")
  
  if movieInfo:
    yearElement = movieInfo.find("h2")
    if yearElement:
      yearText = yearElement.text
      if( yearText and (len(yearText)>=4) and yearText[:4].isnumeric ):
        year = yearText[:4]

  return year


def getMovieGenres( movieSoup ):
  """ Returns list of string with the genres of the movie """

  genresList = []
  movieInfo = movieSoup.find("div", id="movie-info")
  
  if movieInfo:
    elements_h2 = movieInfo.find_all("h2")
    if elements_h2 and len(elements_h2)>1:
      genresText = elements_h2[1].text
      genresList = (genresText).split(" / ")
      
  return genresList


def getMovieSynopsis( movieSoup ):

  synopsis = ""

  synopsis_div = movieSoup.find("div", id="synopsis")
  
  if synopsis_div:
    synopsis_p = synopsis_div.find("p")
    if synopsis_p:
      synopsis = synopsis_p.text
  
  return synopsis


def getMovieRankingInfo( movieSoup ):
  """ Returns tuple of strings with (likes,RottenTomatoesCritics,RottenTomatoesAudience,IMDb_Rating) """

  likes, RottenTomatoesCritics, RottenTomatoesAudience, IMDb_Rating = "","","",""

  ratingInfo = movieSoup.findAll("div", class_="rating-row")
  cantidad = len(ratingInfo)

  if not ratingInfo:
    return (likes, RottenTomatoesCritics, RottenTomatoesAudience, IMDb_Rating)
  
  likes_span = ratingInfo[0].find("span", id="movie-likes")
  if likes_span:
    likes = likes_span.text

  
  for i in range(1,cantidad):
    elem_div = ratingInfo[i]
    elem_a = elem_div.find("a")
    
    if not elem_a:
      continue
    
    attr_title = elem_a.attrs["title"]
    data = ""
    elem_span = elem_div.find("span")
    if elem_span and (elem_span.text)[0].isnumeric():
      data = elem_span.text
    if data.endswith("%"):
      data = data[:-1]

    if attr_title and data:
      if "rotten tomatoes critics" in attr_title.lower():
        RottenTomatoesCritics = data

      elif "rotten tomatoes audience" in attr_title.lower():
        RottenTomatoesAudience = data
      
      elif "imdb" in attr_title.lower():
        IMDb_Rating = data
  

  return (likes, RottenTomatoesCritics, RottenTomatoesAudience, IMDb_Rating)


def getRelatedMoviesLinks( movieSoup ):
  """ Return a list of string with links of movies """

  links = []
  relatedMoviesElement = movieSoup.find("div", id="movie-related")

  if relatedMoviesElement:
    linksElements = relatedMoviesElement.find_all("a")

    if linksElements:
      for element in linksElements:
        links.append( element.attrs["href"] )

  return links


def getRelatedMovieTitles( movieSoup ):
  """ Return a list of strings with the titles of the related movies """

  links = getRelatedMoviesLinks( movieSoup )
  relatedTitles = []

  for link in links:

    relatedMoviePage = requests.get(link)

    if ( relatedMoviePage.status_code != 200 ):
      continue

    relatedMovieSoup = BeautifulSoup(relatedMoviePage.content, "html.parser")

    title = getMovieTitle(relatedMovieSoup)
    if title:
      relatedTitles.append(title)

  
  return relatedTitles


def getDirectors( movieSoup ):

  directors_div = movieSoup.find("div", class_="directors")
  if not directors_div:
    return tuple()

  directors_span = directors_div.findAll("span", itemprop="name")
  if not directors_span:
    return tuple()

  directors = []
  for elem in directors_span:
    directors.append(elem.text)

  return tuple(directors)


def getActors( movieSoup ):

  actors_table = movieSoup.find("div", class_="actors")
  if not actors_table:
    return tuple()

  actors_divs = actors_table.findAll("div", class_="list-cast")
  if not actors_divs:
    return tuple()

  actors = []

  for div in actors_divs:

    if div and div.text:
      actorInfoStr = (div.text).strip()
      actorInfo = actorInfoStr.split(" as ")
      
      if len(actorInfo) == 2:
        actors.append(tuple(actorInfo))

  return tuple(actors)

def getMovieLinks( initPage ):
  """ Input:  initPage: requets Response object with status_code=200 
      Output: str-list with links of the movies
  """

  initPageSoup = BeautifulSoup(initPage.content, "html.parser")

  movies_a_elements = initPageSoup.findAll("a", class_="browse-movie-link")

  movieLinks = []

  for element in movies_a_elements:
    actualLink = element.attrs["href"]
    movieLinks.append(actualLink)

  return movieLinks


def loadMovieData ( movieSoup, link:str, movieData:dict, keys:tuple ):
  """ Input:  movieSoup:BeautifulSoup object
              link:str links of the film page
              movieData: empty dictionary to be loaded
              keys: tuple with dictionery keys
              webDriver: Selenium driver
  
  keys = ("Title","Year","Synopsis","Genres","Link","Comments",
      "Related Movies","Likes","RTCritics %","RTAudience %","IMDb",
      "Directors", "Actors")
  """

  title = getMovieTitle(movieSoup)
  year = getMovieYear(movieSoup)
  genres = getMovieGenres(movieSoup)
  synopsis = getMovieSynopsis(movieSoup)

  likes, RottenTomatoesCritics, RottenTomatoesAudience, IMDb_Rating = getMovieRankingInfo(movieSoup)
  relatedMoviesTitles = getRelatedMovieTitles(movieSoup)
  comments = getFirstComments(link)
  directors = getDirectors(movieSoup)
  actors = getActors(movieSoup)
  
  values = [title, year, synopsis, genres, link, comments, relatedMoviesTitles]
  values.extend( [likes, RottenTomatoesCritics, RottenTomatoesAudience, IMDb_Rating] )
  values.extend( [directors, actors] )

  for key, value in zip(keys, values):
    movieData[key] = value


def loadMovies( movieLinks:list, movieList:list ):
  """ Input:  movieLinks: str-list with links of movies
              movieList: list that contains/will contain Movie objects
              webDriver: selenium driver """

  movieData = dict()
  keys = ("Title","Year","Synopsis","Genres","Link","Comments","Related Movies","Likes","RTCritics %","RTAudience %","IMDb","Directors","Actors")


  for link in movieLinks:

    moviePage = requests.get(link)

    if ( moviePage.status_code != 200 ):
      continue

    movieSoup = BeautifulSoup(moviePage.content, "html.parser")

    movieData.clear()

    loadMovieData( movieSoup, link, movieData, keys )
  
    movie = Movie( movieData )

    movieList.append(movie)
  

  return keys

def createDataFrame( movieList:list, labels:list ):
  """ Input:  movieList: list that contains Movie objects
              labels: str-list with the labels of the dataframe 
      Return: DataFrame created
  """

  tableData = []

  for movie in movieList:
    movieData = []

    moviePrimaryData = list( movie.getPrimaryData() )
    movieSecondaryData = list( movie.getSecondaryData() )
    movieRankingsInfo = list( movie.getRankingsData() )
    movieCastData = list( movie.getCast() )

    movieData.extend( moviePrimaryData )
    movieData.extend( movieSecondaryData )
    movieData.extend( movieRankingsInfo )
    movieData.extend( movieCastData )

    tableData.append( movieData )
  
  movies_df = pd.DataFrame( tableData, columns=labels )

  return movies_df


def saveDFtoCSV( dataFrame, filename:str ):
  
  dataFrame.to_csv(filename, index=False)

def main():


  url = "https://yts.mx/"
  initPage = requests.get(url)

  if ( initPage.status_code != 200 ):
    print( "Error while requesting url: ", url )
    return -1
  
  movieLinks = getMovieLinks( initPage )

  movieList = []
  keys = loadMovies( movieLinks, movieList )

  moviesDataFrame = createDataFrame( movieList, keys )

  print(moviesDataFrame)

  saveDFtoCSV( moviesDataFrame, "movies_info.csv" )



  return 0

main()