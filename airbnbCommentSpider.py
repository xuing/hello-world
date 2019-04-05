# -*- coding: utf-8 -*-

import requests,re,json
import csv
from urllib import parse

def myRequestGet(url,num_retries=5):
    try:
        html = requests.get(url,timeout=8)
    except Exception as e :
        print('出错重试 {0}'.format(e))
        response = None
        if num_retries > 0:
            return myRequestGet(url, num_retries-1)
    return html

def getHouseNumber(url):

    html = myRequestGet(url)

    data = html.text

    jsonData = json.loads(data)

    #构造正则，获取remarketing_ids

    urlbase=re.search('"remarketing_ids":\[(.*?)\],',data)

    #将其放入一个列表return回去主函数

    url=[]

    urlNumber=''

    for each in urlbase.group(1):

        if each==",":
            url.append(urlNumber)

            urlNumber=''
        
        else:
            urlNumber=urlNumber+each

    print()
    if jsonData['explore_tabs'][0]['pagination_metadata'].get('has_next_page') ==  False:
        print("到尾页了")
        url.append('end')
   
    return url

def getHouseInformation(urlNumber):
    
    # 评论
    print("爬取房间id为"+urlNumber+"的评论")
    Commen = ''
    ALL_Information=[]

    for each in range(100):

        #一次爬取100条评论
        CommenUrl = 'https://zh.airbnb.com/api/v2/reviews?key=d306zoyjsyarp7ifhu67rjxn52tv0t20&currency=CNY&locale=zh&listing_id='+str(urlNumber)+'&role=guest&_format=for_p3&_limit=100&_offset=' + str(each * 100) + '&_order=language_country'

        CommenHtml=myRequestGet(CommenUrl)
        
        if CommenHtml.status_code==200:

            Commendata = json.loads(CommenHtml.text)
    
            count = Commendata['metadata'].get('reviews_count')
            
            if count < each * 100:
                print("共"+str(count)+"条")
                break

            for i in Commendata['reviews']:

                #Commen = Commen + i.get('comments') + '\n'
                ALL_Information.append(i.get('comments'))
        else:

            break

    #ALL_Information.append(Commen)

    return ALL_Information

def main(queryStr):

    flag = True
    i = 0
    try:
        out = open('comment.csv', 'w', newline='', encoding='utf-8-sig')
        csv_write = csv.writer(out, dialect='excel')
        
        while flag:
            #一次爬取50个
            HouseNumberUrl="https://zh.airbnb.com/api/v2/explore_tabs?_format=for_explore_search_web&_intents=p1&allow_override%5B%5D=&amenities%5B%5D=8&auto_ib=true&click_referer=t%3ASEE_ALL%7Csid%3Af87f96e6-b3ae-4376-82d1-67ade258d439%7Cst%3AMATCHA_HOME_WITH_POPULAR_AMENITY&client_session_id=a4de7caa-193d-4352-bde2-68d9e4755688&currency=HKD&experiences_per_grid=20&fetch_filters=true&guidebooks_per_grid=20&has_zero_guest_treatment=true&is_guided_search=true&is_new_cards_experiment=true&is_standard_search=true&items_offset="+str(50*i)+"&items_per_grid=50&key=d306zoyjsyarp7ifhu67rjxn52tv0t20&locale=en&luxury_pre_launch=false&metadata_only=false&query="+parse.quote(queryStr)+"&query_understanding_enabled=true&refinement_paths%5B%5D=%2Fhomes&s_tag=1izKAJRg&satori_version=1.1.0&screen_size=large&search_type=PAGINATION&section_offset=7&selected_tab_id=home_tab&show_groupings=true&supports_for_you_v3=true&timezone_offset=480&title_type=NONE&version=1.4.5"
            for number in getHouseNumber(HouseNumberUrl):
                if number == 'end':
                    flag = False
                    
                #print("number:"+number+" i:"+str(i*50))

                stu2=getHouseInformation(number)
                    
                csv_write.writerow(stu2)
                    
            i = i + 1
    finally:
        if out:
            out.close()
 
 
if __name__ == '__main__':

    out = open('comment.csv', 'a', newline='', encoding='utf-8-sig')

    csv_write = csv.writer(out, dialect='excel')

    main("三亚")
    
    print("全部完成")
