# -*- coding:utf8 -*-
import requests
import time
import re
import math
from lxml import etree
import urllib
import json
import sys
reload(sys)
sys.setdefaultencoding('utf8')

def get_retweet(tweet_ID,SUB):
    user_agent={'User-agent':'spider'}
    s = requests.Session()
    retweets=[]
    url='http://weibo.com/aj/v6/mblog/info/big?ajwvr=6&id='+tweet_ID+'&filter=hot'
    res=s.get(url,cookies={'SUB':SUB})
    json_coder= json.JSONDecoder()
    codered=json_coder.decode(res.text)
    hot_retweet_number=int(codered['data']['count'])
    hot_page_number=int(codered['data']['page']['totalpage'])
    if hot_retweet_number!=0:
        for i in range(1,hot_page_number+1):
            url='http://weibo.com/aj/v6/mblog/info/big?ajwvr=6&id='+tweet_ID+'&filter=hot&page='+str(i)
            res=s.get(url,cookies={'SUB':SUB})
            json_coder= json.JSONDecoder()
            codered=json_coder.decode(res.text)
            raw = codered['data']['html']
            ww=etree.HTML(raw)
            tree=ww.xpath('//div[@mid]')
            #print '------------------------------------------hot retweet',len(tree)
            for a in range(len(tree)):
                #print '---'*20
                retweets.append({})
                retweet_ID=tree[a].get('mid')
                #print 'retweet_ID:',tree[a].get('mid')
                retweets[-1]['retweet_ID']=tree[a].get('mid')
                b=tree[a].xpath('.//div[@class="WB_text"]//a[@node-type="name"]')[0]
                #print 'retweeter_ID: ',b.get('usercard').strip('id=')
                #print 'retweeter_name:',b.text
                retweets[-1]['retweeter_ID']=b.get('usercard').strip('id=')
                retweets[-1]['retweeter_name']=b.text
                #verify
                b=tree[a].xpath('.//div[@class="WB_text"]//a[@href="http://company.verified.weibo.com/bluev/verify/index?from=feedv"]')
                if b:
                    #print 'retweeter_Verified: ', b[0].xpath('./i/@title')[0]
                    retweets[-1]['retweeter_Verified']=b[0].xpath('./i/@title')[0]
                else:
                    b=tree[a].xpath('.//div[@class="WB_text"]//a[@href="http://verified.weibo.com/verify"]')
                    if b:
                        #print 'retweeter_Verified: ', b[0].xpath('./i/@title')[0]
                        retweets[-1]['retweeter_Verified']=b[0].xpath('./i/@title')[0]
                #VIP
                b=tree[a].xpath('.//div[@class="WB_text"]//a[@action-type="ignore_list"]')
                if b:
                    #print 'retweeter_VIP:',b[0].xpath('./em/@class')[0][-1]
                    retweets[-1]['retweeter_VIP']=b[0].xpath('./em/@class')[0][-1]
                #retweet content:
                b=tree[a].xpath('.//div[@class="WB_text"]//span[@node-type="text"]//text()')
                content=''.join(b)
                content=content.strip()
                #print 'retweet_content:',content
                retweets[-1]['retweet_content']=content
                #topic
                b=tree[a].xpath('.//div[@class="WB_text"]//a[@class="a_topic"]')
                if b:
                    retweets[-1]['topic']=[]
                    for c in b:
                        retweets[-1]['topic'].append({})
                        #print 'hot topic: ', c.text.strip('#'), c.get('href')
                        retweets[-1]['topic'][-1]['name']=c.text.strip('#')
                        retweets[-1]['topic'][-1]['url']=c.get('href')
                #link
                b=tree[a].xpath('.//div[@class="WB_text"]//a[@action-type="feed_list_url"]')
                if b:
                    retweets[-1]['link']=[]
                    for c in b:
                        retweets[-1]['link'].append({})
                        #print 'hot topic: ', c.text.strip('#'), c.get('href')
                        retweets[-1]['link'][-1]['name']=c.get('title')
                        retweets[-1]['link'][-1]['url']=c.get('href')
                #mention
                b=tree[a].xpath('.//div[@class="WB_text"]//a[@extra-data="type=atname"]')
                if b:
                    retweets[-1]['mention']=[]
                    for c in b:
                        retweets[-1]['mention'].append({})
                        #print 'mentioned user: ',c.get('usercard').strip('name='), c.get('href')
                        retweets[-1]['mention'][-1]['name']=c.get('usercard').strip('name=')
                        retweets[-1]['mention'][-1]['url']=c.get('href')
                b=tree[a].xpath('.//div[@class="WB_text"]//a[@imagecard]/@alt')
                if b:
                    retweets[-1]['image']=[]
                    for c in b:
                        #print 'image:',c
                        retweets[-1]['image'].append(c)
                #face
                b=tree[a].xpath('.//div[@class="WB_text"]//img[@type="face"]/@title')
                if b:
                    retweets[-1]['face']=[]
                    for c in b:
                        #print 'face:',c
                        retweets[-1]['face'].append(c)
                b=tree[a].xpath('.//div[@class="WB_from S_txt2"]//a[@node-type="feed_list_item_date"]/@title')[0]
                #print 'retweet_time:',b
                retweets[-1]['retweet_time']=b
                #retweet like
                b=tree[a].xpath('.//div[@class="WB_handle W_fr"]//a[@action-type="forward_like"]//em[2]/text()')[0]
                if (b).isdigit():
                    retweets[-1]['like_num']=int(b)
                    #print 'retweet like:',int(b)
                else:
                    #print 'retweet like:',0
                    retweets[-1]['like_num']=0
                #retweet number
                b=tree[a].xpath('.//div[@class="WB_handle W_fr"]//a[@action-type="feed_list_forward"]/text()')[0]
                if (' ') not in b:
                    retweets[-1]['child_retweet_number']=0
                    #print 'retweet number:',0
                else :
                    #print 'retweet number: ',b.split(' ')[1]
                    retweets[-1]['child_retweet_number']=int(b.split(' ')[1])
                    #child_retweet_list=get_retweet_list(retweet_ID,s,SUB)
                    retweets[-1]['child_retweet_list']=get_retweet_list(retweet_ID,s,SUB)

    url='http://weibo.com/aj/v6/mblog/info/big?ajwvr=6&id='+tweet_ID+'&filter=0'
    res=s.get(url,cookies={'SUB':SUB})
    json_coder= json.JSONDecoder()
    codered=json_coder.decode(res.text)
    raw = codered['data']['html']
    total_page_number=int(codered['data']['page']['totalpage'])
    total_retweet_number=int(codered['data']['count'])
    #print total_page_number
    #print total_retweet_number
    for i in range(1,total_page_number+1):
        url='http://weibo.com/aj/v6/mblog/info/big?ajwvr=6&id='+tweet_ID+'&page='+str(i)
        res=s.get(url,cookies={'SUB':SUB})
        json_coder= json.JSONDecoder()
        codered=json_coder.decode(res.text)
        raw = codered['data']['html']
        ww=etree.HTML(raw)
        tree=ww.xpath('//div[@mid]')
        #print len(tree)
        begin_num=0
        end_num=len(tree)
        if len(tree)>20:
            begin_num=len(tree)-20
        for a in range(begin_num,end_num):
            retweets.append({})
            #print '---'*20
            retweet_ID=tree[a].get('mid')
            #print 'retweet_ID:',tree[a].get('mid')
            retweets[-1]['retweet_ID']=retweet_ID
            b=tree[a].xpath('.//div[@class="WB_text"]//a[@node-type="name"]')[0]
            #print 'retweeter_ID: ',b.get('usercard').strip('id=')
            #print 'retweeter_name:',b.text
            retweets[-1]['retweeter_ID']=b.get('usercard').strip('id=')
            retweets[-1]['retweeter_name']=b.text
            #verify
            b=tree[a].xpath('.//div[@class="WB_text"]//a[@href="http://company.verified.weibo.com/bluev/verify/index?from=feedv"]')
            if b:
                retweets[-1]['retweeter_Verified']=b[0].xpath('./i/@title')[0]
                #print 'retweeter_Verified: ', b[0].xpath('./i/@title')[0]
            else:
                b=tree[a].xpath('.//div[@class="WB_text"]//a[@href="http://verified.weibo.com/verify"]')
                if b:
                    retweets[-1]['retweeter_Verified']=b[0].xpath('./i/@title')[0]
                    #print 'retweeter_Verified: ', b[0].xpath('./i/@title')[0]
            #VIP
            b=tree[a].xpath('.//div[@class="WB_text"]//a[@href="http://vip.weibo.com/personal?from=main"]')
            if b:
                retweets[-1]['retweeter_VIP']=b[0].xpath('./em/@class')[0][-1]
                #print 'retweeter_VIP:',b[0].xpath('./em/@class')[0][-1]
            #retweet content:
            b=tree[a].xpath('.//div[@class="WB_text"]//span[@node-type="text"]//text()')
            content=''.join(b)
            content=content.strip()
            #print 'retweet_content:',content
            retweets[-1]['retweet_content']=content
            #topic
            b=tree[a].xpath('.//div[@class="WB_text"]//a[@class="a_topic"]')
            if b:
                retweets[-1]['topic']=[]
                for c in b:
                    retweets[-1]['topic'].append({})
                    #print 'hot topic: ', c.text.strip('#'), c.get('href')
                    retweets[-1]['topic'][-1]['name']=c.text.strip('#')
                    retweets[-1]['topic'][-1]['url']=c.get('href')
            #link
            b=tree[a].xpath('.//div[@class="WB_text"]//a[@action-type="feed_list_url"]')
            if b:
                retweets[-1]['link']=[]
                for c in b:
                    retweets[-1]['link'].append({})
                    #print 'hot topic: ', c.text.strip('#'), c.get('href')
                    retweets[-1]['link'][-1]['name']=c.get('title')
                    retweets[-1]['link'][-1]['url']=c.get('href')
            #mention
            b=tree[a].xpath('.//div[@class="WB_text"]//a[@extra-data="type=atname"]')
            if b:
                retweets[-1]['mention']=[]
                for c in b:
                    retweets[-1]['mention'].append({})
                    #print 'mentioned user: ',c.get('usercard').strip('name='), c.get('href')
                    retweets[-1]['mention'][-1]['name']=c.get('usercard').strip('name=')
                    retweets[-1]['mention'][-1]['url']=c.get('href')
            b=tree[a].xpath('.//div[@class="WB_text"]//a[@imagecard]/@alt')
            if b:
                retweets[-1]['image']=[]
                for c in b:
                    #print 'image:',c
                    retweets[-1]['image'].append(c)
            #face
            b=tree[a].xpath('.//div[@class="WB_text"]//img[@type="face"]/@title')
            if b:
                retweets[-1]['face']=[]
                for c in b:
                    retweets[-1]['face'].append(c)
                    #print 'face:',c
            b=tree[a].xpath('.//div[@class="WB_from S_txt2"]//a[@node-type="feed_list_item_date"]/@title')[0]
            #print 'retweet_time:',b
            retweets[-1]['retweet_time']=b
            #retweet like
            b=tree[a].xpath('.//div[@class="WB_handle W_fr"]//a[@action-type="forward_like"]//em[2]/text()')[0]
            if (b).isdigit():
                #print 'retweet like:',int(b)
                retweets[-1]['like_num']=int(b)
            else:
                #print 'retweet like:',0
                retweets[-1]['like_num']=0
            #retweet number
            b=tree[a].xpath('.//div[@class="WB_handle W_fr"]//a[@action-type="feed_list_forward"]/text()')[0]
            if (' ') not in b:
                #print 'retweet number:',0
                retweets[-1]['child_retweet_number']=0
            else :
                print 'retweet number: ',b.split(' ')[1]
                child_retweet_list=get_retweet_list(retweet_ID,s,SUB)
                #retweets[-1]['child_retweet_number']=int(b.split(' ')[1])
                retweets[-1]['child_retweet_list']=get_retweet_list(retweet_ID,s,SUB)
    return retweets
def get_retweet_list(tweet_ID,s,SUB):
    retweet_list=[]
    url='http://weibo.com/aj/v6/mblog/info/big?ajwvr=6&id='+tweet_ID+'&filter=hot'
    res=s.get(url,cookies={'SUB':SUB})
    json_coder= json.JSONDecoder()
    codered=json_coder.decode(res.text)
    hot_retweet_number=int(codered['data']['count'])
    hot_page_number=int(codered['data']['page']['totalpage'])
    if hot_retweet_number!=0:
        for i in range(1,hot_page_number+1):
            url='http://weibo.com/aj/v6/mblog/info/big?ajwvr=6&id='+tweet_ID+'&filter=hot&page='+str(i)
            res=s.get(url,cookies={'SUB':SUB})
            json_coder= json.JSONDecoder()
            codered=json_coder.decode(res.text)
            raw = codered['data']['html']
            ww=etree.HTML(raw)
            tree=ww.xpath('//div[@mid]')
            #print '------------------------------------------hot retweet',len(tree)
            for a in range(len(tree)):
                retweet_list.append({})
                #print '---'*20
                #retweet_ID=tree[a].get('mid')
                retweet_list[-1]['retweet_ID']=tree[a].get('mid')
                #print 'retweet_ID:',tree[a].get('mid')
                b=tree[a].xpath('.//div[@class="WB_text"]//a[@node-type="name"]')[0]
                #print 'retweeter_ID: ',b.get('usercard').strip('id=')
                #print 'retweeter_name:',b.text
                retweet_list[-1]['retweeter_ID']=b.get('usercard').strip('id=')
                b=tree[a].xpath('.//div[@class="WB_from S_txt2"]//a[@node-type="feed_list_item_date"]/@title')[0]
                #print 'retweet_time:',b
                retweet_list[-1]['retweet_time']=b
                # #verify
                # b=tree[a].xpath('.//div[@class="WB_text"]//a[@href="http://company.verified.weibo.com/bluev/verify/index?from=feedv"]')
                # if b:
                #     print 'retweeter_Verified: ', b[0].xpath('./i/@title')[0]
                # else:
                #     b=tree[a].xpath('.//div[@class="WB_text"]//a[@href="http://verified.weibo.com/verify"]')
                #     if b:
                #         print 'retweeter_Verified: ', b[0].xpath('./i/@title')[0]
                # #VIP
                # b=tree[a].xpath('.//div[@class="WB_text"]//a[@action-type="ignore_list"]')
                # if b:
                #     print 'retweeter_VIP:',b[0].xpath('./em/@class')[0][-1]
                # #retweet content:
                # b=tree[a].xpath('.//div[@class="WB_text"]//span[@node-type="text"]//text()')
                # content=''.join(b)
                # content=content.strip()
                # print 'retweet_content:',content
                # #topic
                # b=tree[a].xpath('.//div[@class="WB_text"]//a[@class="a_topic"]')
                # if b:
                #     for c in b:
                #         print 'hot topic: ', c.text.strip('#'), c.get('href')
                # #mention
                # b=tree[a].xpath('.//div[@class="WB_text"]//a[@extra-data="type=atname"]')
                # if b:
                #     for c in b:
                #         print 'mentioned user: ',c.get('usercard').strip('name='), c.get('href')
                # b=tree[a].xpath('.//div[@class="WB_text"]//a[@imagecard]/@alt')
                # if b:
                #     for c in b:
                #         print 'image:',c
                # #face
                # b=tree[a].xpath('.//div[@class="WB_text"]//img[@type="face"]/@title')
                # if b:
                #     for c in b:
                #         print 'face:',c
                # b=tree[a].xpath('.//div[@class="WB_from S_txt2"]//a[@node-type="feed_list_item_date"]/@title')[0]
                # print 'retweet_time:',b
                # #retweet like
                # b=tree[a].xpath('.//div[@class="WB_handle W_fr"]//a[@action-type="forward_like"]//em[2]/text()')[0]
                # if (b).isdigit():
                #     print 'retweet like:',int(b)
                # else:
                #     print 'retweet like:',0
                # #retweet number
                # b=tree[a].xpath('.//div[@class="WB_handle W_fr"]//a[@action-type="feed_list_forward"]/text()')[0]
                # if (' ') not in b:
                #     print 'retweet number:',0
                # else :
                #     print 'retweet number: ',b.split(' ')[1]
                #     #retweet_list=get_retweet(retweet_ID,SUB)

    url='http://weibo.com/aj/v6/mblog/info/big?ajwvr=6&id='+tweet_ID+'&filter=0'
    res=s.get(url,cookies={'SUB':SUB})
    json_coder= json.JSONDecoder()
    codered=json_coder.decode(res.text)
    raw = codered['data']['html']
    total_page_number=int(codered['data']['page']['totalpage'])
    total_retweet_number=int(codered['data']['count'])
    #print total_page_number
    #print total_retweet_number
    for i in range(1,total_page_number+1):
        url='http://weibo.com/aj/v6/mblog/info/big?ajwvr=6&id='+tweet_ID+'&page='+str(i)
        res=s.get(url,cookies={'SUB':SUB})
        json_coder= json.JSONDecoder()
        codered=json_coder.decode(res.text)
        raw = codered['data']['html']
        ww=etree.HTML(raw)
        tree=ww.xpath('//div[@mid]')
        #print len(tree)
        begin_num=0
        end_num=len(tree)
        if len(tree)>20:
            begin_num=len(tree)-20
        for a in range(begin_num,end_num):
            retweet_list.append({})
            #print '---'*20
            #retweet_ID=tree[a].get('mid')
            #print 'retweet_ID:',tree[a].get('mid')
            retweet_list[-1]['retweet_ID']=tree[a].get('mid')
            b=tree[a].xpath('.//div[@class="WB_text"]//a[@node-type="name"]')[0]
            #print 'retweeter_ID: ',b.get('usercard').strip('id=')
            #print 'retweeter_name:',b.text
            retweet_list[-1]['retweeter_ID']=b.get('usercard').strip('id=')
            b=tree[a].xpath('.//div[@class="WB_from S_txt2"]//a[@node-type="feed_list_item_date"]/@title')[0]
            #print 'retweet_time:',b
            retweet_list[-1]['retweet_time']=b
            # #verify
            # b=tree[a].xpath('.//div[@class="WB_text"]//a[@href="http://company.verified.weibo.com/bluev/verify/index?from=feedv"]')
            # if b:
            #     print 'retweeter_Verified: ', b[0].xpath('./i/@title')[0]
            # else:
            #     b=tree[a].xpath('.//div[@class="WB_text"]//a[@href="http://verified.weibo.com/verify"]')
            #     if b:
            #         print 'retweeter_Verified: ', b[0].xpath('./i/@title')[0]
            # #VIP
            # b=tree[a].xpath('.//div[@class="WB_text"]//a[@href="http://vip.weibo.com/personal?from=main"]')
            # if b:
            #     print 'retweeter_VIP:',b[0].xpath('./em/@class')[0][-1]
            # #retweet content:
            # b=tree[a].xpath('.//div[@class="WB_text"]//span[@node-type="text"]//text()')
            # content=''.join(b)
            # content=content.strip()
            # print 'retweet_content:',content
            # #topic
            # b=tree[a].xpath('.//div[@class="WB_text"]//a[@class="a_topic"]')
            # if b:
            #     for c in b:
            #         print 'hot topic: ', c.text.strip('#'), c.get('href')
            # #mention
            # b=tree[a].xpath('.//div[@class="WB_text"]//a[@extra-data="type=atname"]')
            # if b:
            #     for c in b:
            #         print 'mentioned user: ',c.get('usercard').strip('name='), c.get('href')
            # b=tree[a].xpath('.//div[@class="WB_text"]//a[@imagecard]/@alt')
            # if b:
            #     for c in b:
            #         print 'image:',c
            # #face
            # b=tree[a].xpath('.//div[@class="WB_text"]//img[@type="face"]/@title')
            # if b:
            #     for c in b:
            #         print 'face:',c
            # b=tree[a].xpath('.//div[@class="WB_from S_txt2"]//a[@node-type="feed_list_item_date"]/@title')[0]
            # print 'retweet_time:',b
            # #retweet like
            # b=tree[a].xpath('.//div[@class="WB_handle W_fr"]//a[@action-type="forward_like"]//em[2]/text()')[0]
            # if (b).isdigit():
            #     print 'retweet like:',int(b)
            # else:
            #     print 'retweet like:',0
            # #retweet number
            # b=tree[a].xpath('.//div[@class="WB_handle W_fr"]//a[@action-type="feed_list_forward"]/text()')[0]
            # if (' ') not in b:
            #     print 'retweet number:',0
            # else :
            #     print 'retweet number: ',b.split(' ')[1]
            #     #retweet_list=get_retweet(retweet_ID,SUB)
    return retweet_list
if __name__ == '__main__':
    #this is the user ID
    ID='4106640086876351'
    #this is the cookie key and value you have to add to the request
    SUB='_2AkMvnYHZdcPhrAZXnPkQzGnhaYRH-jycSOgvAn7uJhMyAxgv7nExqSVFXD9BUcx5oZy01um07nYYpXXqrg..'
    retweets=get_retweet(ID,SUB)
    #you can use this code to convert dict to json type
    result=json.dumps(retweets, ensure_ascii = False, indent = 4)
    #write in the file
    f=open('./test.txt','w')
    f.write(result.strip()+'\n')
    f.close()


