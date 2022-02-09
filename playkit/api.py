import requests

from bs4 import BeautifulSoup


def search(keyword="",category="apps",country="us",pricing="all",rating="all",format="dict",proxies=None):
    requests.packages.urllib3.disable_warnings()
    priceMap = {"all":0,"free":1,"paid":2,"All":0,"Free":1,"Paid":2}
    ratingsMap = {"all":0,"4+":1,"All":0}
    response = {"status":"OK","error":None,"results":[]}
    try:
        payload = {'q': keyword, 'c': category,'gl': country,"price":priceMap[pricing],"rating":ratingsMap[rating]}
    except KeyError as e:
        response = {"status":"Failed","error":e,"results":[]}
        return response



    url = "https://play.google.com/store/search?"
    try:
        if proxies:
            htmlresponse = requests.get(url,params = payload,proxies=proxies)
        else:
            htmlresponse = requests.get(url,params = payload)

        htmlresponse = BeautifulSoup(htmlresponse.text, 'html.parser')

        contents = htmlresponse.find_all("div",class_="id-card-list" )[0].findAll("div", { "class" : "card-content id-track-click id-track-impression" })
        
        for content in contents:
            result = {}
            result["name"] = content.find("a", {"class":"title"})["title"]
            result["id"] = content.find("span", {"class":"preview-overlay-container"})["data-docid"]
            result["developer"] = content.find("a", {"class":"subtitle"})["title"]
            result["description"] = content.find("div", {"class":"description"}).getText()
            try:
                result["rating"] = content.find("div", {"class":"tiny-star star-rating-non-editable-container"})["aria-label"]
            except TypeError:
                result["rating"] = "Not rated"
            result["price"] = content.findAll("span", {"class":"display-price"})[0].getText()
            result["largeImageUrl"] = content.find("img", {"class":"cover-image"})["data-cover-large"]
            result["smallImageUrl"] = content.find("img", {"class":"cover-image"})["data-cover-small"]
            response["results"].append(result)
        return response
    except Exception as e:
            response["error"] = e
            response["status"] = "Failed"
            return response

def appdetails(identifier="",format="dict",proxies=None):
    requests.packages.urllib3.disable_warnings()
    response = {"status":"OK","error":None,"results":{}}
    try:
        payload = {'id': identifier}
    except KeyError as e:
        response = {"status":"Failed","error":e,"results":{}}
        return response


    
    url = "https://play.google.com/store/apps/details?"
    try:
        if proxies:
            htmlresponse = requests.get(url,params = payload,proxies=proxies)
        else:
            htmlresponse = requests.get(url,params = payload)
        result = {}
        htmlresponse = BeautifulSoup(htmlresponse.text, 'html.parser')
        contents = htmlresponse.find("div", { "class" : "details-wrapper apps square-cover id-track-partial-impression id-deep-link-item" })        
        result["id"] = contents["data-docid"]
        result["name"] =  contents.find("div",{"class":"document-title"}).getText()
        price =  contents.find("meta",{"itemprop":"price"})["content"].replace(u'\xa0',u' ')
        result["price"] = price if price !='0' else 'Free'
        result["category"] =  contents.find("a",{"class":"document-subtitle category"}).getText()
        result["developer"] = contents.find("a",{"class":"document-subtitle primary"}).getText()
        result["description"] = contents.find("div",{"class":"show-more-content text-body"}).getText()
        result["mediumImageUrl"] =  contents.find("img",{"class":"cover-image"})['src']
        try:
            result["rating"] = contents.find("div", {"class":"tiny-star star-rating-non-editable-container"})["aria-label"]
        except TypeError:
            result["rating"] = "Not rated"
        try:
            res = contents.find("div",{"class":"thumbnails","data-expand-target":"thumbnails"}).findAll('img',{"class":"screenshot"})
            result['screenshots'] =[]
            for screenshot in res:
                result['screenshots'].append(screenshot["src"])
        except Exception as e:
            result['screenshots'] =[]
        try:
            reviewContents = htmlresponse.find("div", { "class" : "details-wrapper apps" })
            result["ratingValue"] = reviewContents.find("meta",{"itemprop":"ratingValue"})["content"]
            reviewContent = reviewContents.find("div",{"class":"preview-reviews multicol"}).findAll("div",{"featured-review"})
            result['review'] =[]
            for review in reviewContent:
                reviewData = {}
                reviewData["author"] =  review.find("span",{"class":"author-name"}).getText()
                reviewData["title"] = review.find("span",{"class":"review-title"}).getText()
                reviewData["text"] = review.find("div",{"class":"review-text"}).getText()
                reviewData["rating"] = review.find("div",{"class":"tiny-star star-rating-non-editable-container"})["aria-label"]
                reviewData["link"] = review.find("div",{"class":"author"}).find("a")["href"]
                result["review"].append(reviewData)
        except AttributeError:
            result["ratingValue"] = None
            result["review"] = []
        except Exception as e:
            print e

        try:
            additionalinfo = htmlresponse.find("div", { "class" : "details-section metadata" })
            result["datePublished"] = additionalinfo.find("div",{"itemprop":"datePublished"}).getText()
            result["fileSize"] = additionalinfo.find("div",{"itemprop":"fileSize"}).getText()
            result["currentVersion"] = additionalinfo.find("div",{"itemprop":"softwareVersion"}).getText()
            result["requiresAndroid"] = additionalinfo.find("div",{"itemprop":"operatingSystems"}).getText().strip()
        except Exception as e:
            print e

        response["results"] = result
    except Exception as e:
        response["error"] = e
        response["status"] = "Failed"
        response["results"] = result
    return response
