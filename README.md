# Movies_Web_Scraping_Test
Some web scraping with python in the page 'https://yts.mx/' to take movies data.
I'm just learning about web scraping using BeautifulSoup and Selenium in Python.


This is a small test about web scraping. I used the web "https://yts.mx/" that have some films data.
I collected some data like title, year, rankings, and so on.
A Movie object order the datain attributes.
The data were packed in a Pandas DataFrame and then saved in a csv file.
The use of Selenium is prepared to be used in Chrome Browser.

The repository contains the notebook file, to use and test interactively, and the python file to execute directry.
The CSV file contains the output of the code.


Problems:
  When I try to get the comments using Selenium, theoretically I should be able to get the first 30 comments, but the number of elements taken varies.
  So most of the times I get few comments.
