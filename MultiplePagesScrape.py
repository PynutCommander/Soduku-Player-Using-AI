import bs4 as bs
import re
import xlsxwriter
import urllib.request
import pandas as pd
from collections import Counter
import math

class scraper(object):
    def __init__(self, urlName=None, multipleURL= None, tag=None):
        self.urlName = urlName
        self.sauce = None
        self.soupe = None
        self.allLinks = []
        self.brokenLinks = []
        self.countLinks = []
        self.source = []
        self.types = None
        self.target = None
        self.occurances = None
        self.percentages = None
        self.df = pd.DataFrame()
        self.BKlinks = pd.DataFrame()
        self.perOcc = pd.DataFrame()
        if(multipleURL == None):
            self.cookSauce()
            self.cookSoup()
            self.extractDates()
            self.allLinks = self.getLinks()
            self.brokenLinks = self.getBrokenLinks(self.allLinks)
            self.countLinks = self.getCountWorkingLinks(self.allLinks)
            self.source = self.getSource(self.allLinks)
            self.types, self.target = self.getTypesAndTarget(self.allLinks)
            self.occurances, self.percentages = self.calculateOccurance(self.types)
            self.designDataFrame()
            urlName = self.getURLname(tag = tag)
            self.createXlsx(urlName)
        else:
            self.sauce = None
            self.soupe = None
            self.allLinks = []
            self.brokenLinks = []
            self.countLinks = []
            self.source = []
            self.types = []
            self.target = []
            self.occurances = []
            self.percentages = []
            self.df = pd.DataFrame()
            self.BKlinks = pd.DataFrame()
            self.perOcc = pd.DataFrame()
            self.date = []
            for i in range(len(multipleURL)):
                self.urlName = multipleURL[i]
                self.cookSauce()
                self.cookSoup()
                self.allLinks.append(self.getLinks())
                self.brokenLinks.append(self.getBrokenLinks(self.allLinks[i]))
                date = self.extractDates()
                self.source.append(self.getSource(self.allLinks[i]))
                self.date.append(date)
                self.types.append(0)
                self.target.append(0)
                self.types[len(self.types)-1], self.target[len(self.target)-1] = self.getTypesAndTarget(self.allLinks[i])

                # self.occurances.append(0)
                # self.percentages.append(0)
                # self.occurances[len(self.occurances)-1], self.percentages[len(self.percentages)-1] = self.calculateOccurance(self.types[i])



            name = self.getURLname(self.urlName,  tag)
            # self.countedLinks = self.getMultipleCounts()
            self.designMultiplDataFrames2()
            # self.designMultipleDataFrames()
            self.createXlsx(name)


    def extractDates(self):
        date = self.soupe.find("div", {"class":"slideshow_title"})
        if(date == None):
            date = self.soupe.find("h1")
            date = "".join(map(str, date.contents))
        else:
            date = "".join(map(str, date.contents))
        date = date.split(" ")
        counter = len(date)-1
        while counter > 1:
            if(date[counter].isdigit()):
                date = date[counter]
                break
            counter-=1
        return date

    def getURLname(self, name = None, iteration=None, tag=None):
        if name == None:
            urlName = self.urlName.split(".")
            for i in range(len(urlName)):
                if ("www" in urlName[i]):
                    urlName = urlName[i+1]
                    break
            urlName = urlName + str(tag) +".xlsx"
            return urlName
        else:
            name = name.split(".")
            for i in range(len(name)):
                if ("www" in name[i]):
                    name = name[i+1]
                    break
            name = str(name) + "_" + str(iteration) + ".xlsx"
            return name
    def cookSauce(self):
        print("Scraped page :", self.urlName)
        self.sauce = urllib.request.urlopen(self.urlName).read()

    def cookSoup(self):
        self.soupe = bs.BeautifulSoup(self.sauce, "lxml")

    def getLinks(self):
        allLinks = []
        for link in self.soupe.findAll("a", attrs={"href" : re.compile("^http://")}):
            data = link.get("href")
            if(data not in allLinks):
                allLinks.append(data)
        return allLinks

    def getBrokenLinks(self, allLinks):
        com = "com"
        brokenIndex = []
        brokenLinks = []
        size = len(allLinks)
        for i in range(size):
            check = allLinks[i].split(".")
            broken=0
            for j in range(len(check)):
                if (com in check[j]):
                    broken+=1
                    if(broken >= 2):
                        brokenLinks.append(allLinks[i])
                        brokenIndex.append(i)

        remover = False
        for i in range(len(brokenIndex)):
            if(remover == False):
                allLinks.pop(brokenIndex[i])
                remover=True
            else:
                allLinks.pop(brokenIndex[i]-1)
        return brokenLinks

    def getMultipleCounts(self):
        counter = []
        for i in range(len(self.allLinks)):
            counter.append(Counter(self.allLinks[i]))

        totalLinks = {}
        totalLinksIndex = []
        for i in range(len(self.allLinks)):
            for j in range(len(self.allLinks[i])):
                if(self.allLinks[i][j] not in totalLinks):
                    totalLinks[str(self.allLinks[i][j])] = 0
                    totalLinksIndex.append(str(self.allLinks[i][j]))

        totalcounter=  0
        for i in range(len(totalLinks)):
            for j in range(len(counter)):
                totalcounter += counter[j][totalLinksIndex[i]]
            totalLinks[totalLinksIndex[i]] = totalcounter
            totalcounter = 0

        return totalLinks

    def getCountWorkingLinks(self, allLinks):
        countLinks =[]
        for i in range( len(allLinks)):
            countLinks.append(1)
        return countLinks

    def getSource(self, allLinks):
        source = []
        for i in range(len(allLinks)):
            sourceCounter = 0
            for j in range(len(allLinks[i])):
                if(allLinks[i][j] == "/"):
                    sourceCounter+=1
                    if(sourceCounter == 2):
                        if((allLinks[i][j+1] == 'w') and (allLinks[i][j+2] == 'w') and (allLinks[i][j+3] == 'w')):
                            thirdCounter = j+5
                            websiteName = []
                            if ("." in allLinks[i]):
                                while True:
                                    if(allLinks[i][thirdCounter] == "."or (thirdCounter+1 == len(allLinks[i]))):
                                        source.append("".join(map(str, websiteName)))
                                        break
                                    else:
                                        websiteName.append(allLinks[i][thirdCounter])
                                        thirdCounter+=1
                        else:
                            thirdCounter = j+1
                            if("." in allLinks[i]):
                                while True:
                                    if(allLinks[i][thirdCounter] == "." or (thirdCounter+1 == len(allLinks[i]))):
                                        source.append("".join(map(str, websiteName)))
                                        break
                                    else:
                                        websiteName.append(allLinks[i][thirdCounter])
                                        thirdCounter+=1

                            break
        return source

    def getTypesAndTarget(self, allLinks):
        links = []
        for i in range(len(allLinks)):
            links.append(allLinks[i].split("/"))
        typesUnformatted = []
        for i in range(len(links)):
            found= False
            for j in range(len(links[i])):

                if(".com" in links[i][j]):
                    found=True
                    if (j+1 != len(links[i])):
                        if(links[i][j+1] != ""):
                            typesUnformatted.append(links[i][j+1])

                            break
                        else:
                            typesUnformatted.append("Other")
                            break
                    else:
                        typesUnformatted.append("Other")
                        break
            if(found == False):
                typesUnformatted.append("Other")
        # for i in range(len(links)):
        #     if(len(links[i]) > 3):
        #         for j in range(len(links[i])):
        #             if(("www" in links[i][2]) or (".com" in links[i][2])):
        #                 if(len(links[i]) >= 4):
        #                     typesUnformatted.append(links[i][3])
        #                     break
        #                 else:
        #                     typesUnformatted.append("Other")
        #                     break
        #             else:
        #                 typesUnformatted.append("Other")
        #                 break
        #     else:
        #         typesUnformatted.append("Other")
        #
        # targetUnformatted = []
        # print(len(links))
        # for i in range(len(links)):
        #     if(len(links[i]) > 4):
        #         for j in range(len(links[i])):
        #             if(("www" in links[i][j]) or (".com" in links[i][j])):
        #                 if(len(links[i] )>=5):
        #                     targetUnformatted.append(links[i][4])
        #                     break
        #                 else:
        #                     targetUnformatted.append("NotSpecified")
        #                     break
        #     else:
        #         targetUnformatted.append("NotSpecified")





        for i in range(len(typesUnformatted)):
            if(("?" in typesUnformatted[i])):
                formattedWord = []
                for j in range(len(typesUnformatted[i])):
                    if(typesUnformatted[i][j] == "?"):
                        typesUnformatted[i] = "".join(map(str, formattedWord))
                        break
                    else:
                        formattedWord.append(typesUnformatted[i][j])

        for i in range(len(typesUnformatted)):
            if(len(typesUnformatted[i]) > 0):
                if(typesUnformatted[i][0].isalpha() == False):
                    typesUnformatted[i] = "Other"
                if(typesUnformatted[i][0] == "#"):
                    typesUnformatted[i] = "Other"



        targetUnformatted = []
        for i in range(len(links)):
            targetUnformatted.append(links[i][len(links[i])-1])

        for i in range(len(targetUnformatted)):

            if(targetUnformatted[i] == ""):
                targetUnformatted[i] = "NotSpecified"
            if( "www" in targetUnformatted[i]):
                targetUnformatted[i] = targetUnformatted[i].strip("www")
                if(".com" in targetUnformatted[i]):
                    targetUnformatted[i] =targetUnformatted[i].strip(".com")
            if(targetUnformatted[i].isdigit() == True):
                targetUnformatted[i] = links[i][len(links[i])-2]

        return typesUnformatted, targetUnformatted

    def calculateOccurance(self, types):
        occurances = Counter(types)
        percentages = []
        size = len(types)
        listofUsedWords = []
        listofOccurances = []
        for i in range(len(types)):
            word = types[i]
            if(word in listofUsedWords):
                pass
            else:
                percentages.append(float(occurances[types[i]] / size ) * 100)
                listofOccurances.append(types[i])
                listofUsedWords.append(word)


        sum = 0
        for i in range(len(percentages)):
            sum+= percentages[i]
        listofOccurances.append("Grand Total")
        percentages.append(math.floor(sum))

        return listofOccurances, percentages

    def designMultiplDataFrames2(self):
        fullLinks = []
        fullLinksCount = []
        source = []
        types = []
        target = []
        brokenLinks = []
        dates = []
        for i in range(len(self.allLinks)):
            for j in range(len(self.allLinks[i])):
                if (self.allLinks[i][j] not in fullLinks):
                    fullLinks.append(self.allLinks[i][j])
                    fullLinksCount.append(i + 1)
                    dates.append(self.date[i])
                    source.append(self.source[i][j])
                    types.append(self.types[i][j])
                    target.append(self.target[i][j])

        for i in range(len(self.brokenLinks)):
            for j in range(len(self.brokenLinks[i])):
                if (self.brokenLinks[i][j] not in brokenLinks):
                    brokenLinks.append(self.brokenLinks[i][j])

        occurances, percentages = self.calculateOccurance(target)
        self.df["Location"] = fullLinks
        self.df["Count"] = fullLinksCount
        self.df["Source"] = source
        self.df["Types"] = types
        self.df["Target"] = target
        self.df["Date"] = dates
        self.BKlinks["BrokenLinks"] = brokenLinks
        self.perOcc["Occurances"] = occurances
        self.perOcc["Percentages"] = percentages

    def designMultipleDataFrames(self):

        fullLinks = []
        for i in range(len(self.allLinks)):
            for j in range(len(self.allLinks[i])):
                fullLinks.append(self.allLinks[i][j])

        fullLinksCounts = []
        # for i in range(len(fullLinks)):
        #     fullLinksCounts.append(self.countedLinks[str(fullLinks[i])])
        for i in range(len(self.allLinks)):
            for j in range(len(self.allLinks[i])):
                fullLinksCounts.append(i+1)

        source = []
        for i in range(len(self.source)):
            for j in range(len(self.source[i])):
                source.append(self.source[i][j])

        types = []
        for i in range(len(self.types)):
            for j in range(len(self.types[i])):
                types.append(self.types[i][j])

        target = []
        for i in range(len(self.target)):
            for j in range(len(self.target[i])):
                target.append(self.target[i][j])

        brokenLinks = []
        for i in range(len(self.brokenLinks)):
            for j in range(len(self.brokenLinks[i])):
                brokenLinks.append(self.brokenLinks[i][j])

        occurances = []
        for i in range(len(self.occurances)):
            for j in range(len(self.occurances[i])):
                occurances.append(self.occurances[i][j])

        percentages = []
        for i in range(len(self.percentages)):
            for j in range(len(self.percentages[i])):
                percentages.append(self.percentages[i][j])

        self.df["Location"] = fullLinks
        self.df["Count"] = fullLinksCounts
        self.df["Source"] = source
        self.df["Types"] = types
        self.df["Target"] = target
        self.BKlinks["BrokenLinks"] = brokenLinks
        self.perOcc["Occurances"] = occurances
        self.perOcc["Percentages"] = percentages

    def designDataFrame(self):
        self.df["Location"] = self.allLinks
        self.df["Count"] = self.countLinks
        self.df["Source"] = self.source
        self.df["Types"] = self.types
        self.df["Target"] = self.target
        self.BKlinks["BrokenLinks"] = self.brokenLinks
        self.perOcc["Occurances"] = self.occurances
        self.perOcc["Percentages"] = self.percentages


    def createXlsx(self, name=None):
        workbook = xlsxwriter.Workbook(name, options={'strings_to_urls': False})
        worksheet = workbook.add_worksheet()
        worksheet.set_column(0,0,145)
        worksheet.set_column(1,8,75)
        bold = workbook.add_format({"bold": True})
        worksheet.write(0,0,"Location",bold)
        worksheet.write(0,1,"Count",bold)
        worksheet.write(0,2,"Source",bold)
        worksheet.write(0,3,"Type",bold)
        # worksheet.write(0,4,"Target",bold)
        # worksheet.write(0,5,"BrokenLinks",bold)
        # worksheet.write(0,6,"Occurances",bold)
        # worksheet.write(0,7,"Percentages",bold)
        self.writer(worksheet, 1, 0, self.df, "Location")
        self.writer(worksheet, 1, 1, self.df, "Date")
        self.writer(worksheet, 1, 2, self.df, "Source")
        self.writer(worksheet, 1, 3, self.df, "Types")
        # self.writer(worksheet, 1, 4, self.df, "Target")
        # self.writer(worksheet, 1, 5, self.BKlinks, "BrokenLinks")
        # self.writer(worksheet, 1, 6, self.perOcc, "Occurances")
        # self.writer(worksheet, 1, 7, self.perOcc, "Percentages")
        workbook.close()



    def writer(self,worksheet ,x, y, file, data):
        for i in range(len(file[data])):
            worksheet.write(x, y, file[data][i])
            x+=1


def generator(website, initial, max, choice):
    if(choice == 1):
        generatePages = []
        for i in range(max):
            generatePages.append(website.replace(str(initial), str(i+1)))
        return generatePages
    else:
        word = website.split("/")
        generatePages = []
        # for i in range(len(word)):
        #     if word[i] == "":
        #         word[i] = "//"
        fixedWebsite = ""
        arrayWebsite = []
        for i in range (max):
            if(i == 0):
                word[len(word)-1] = ""
                for j in range(len(word)):
                    if(j == 0):
                        arrayWebsite.append(word[j])
                        arrayWebsite.append("/")
                    else:
                        arrayWebsite.append(word[j])
                        arrayWebsite.append("/")
                generatePages.append("".join(map(str, arrayWebsite)))
                arrayWebsite = []
            else:
                word[len(word)-1] = str(i+1)
                for j in range(len(word)):
                    if(j == 0):
                        arrayWebsite.append(word[j])
                        arrayWebsite.append("/")
                    else:
                        arrayWebsite.append(word[j])
                        arrayWebsite.append("/")
                generatePages.append("".join(map(str, arrayWebsite)))
                arrayWebsite = []
        return generatePages




a = "123"
b = "123"
c = "123"

generatePages = []
oldValue = "50"
for i in range(50):
    generatePages.append(a.replace(str(50), str(i+1)))

website2016 = generator(a, 50, 50,1 )
website2015 = generator(c, 2,50, 2)
website2017 = b
listofLinks = []
for i in range(len(website2015)):
    listofLinks.append(website2015[i])
for i in range(len(website2016)):
    listofLinks.append(website2016[i])
listofLinks.append(website2017)
# scrapeData = scraper(multipleURL = website2016, tag="2016")
scrapeData = scraper(multipleURL= listofLinks, tag= "2015_16_17")
# scrapeData = scraper(website2017, tag= "2017")
