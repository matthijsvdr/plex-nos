#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import locale
locale.setlocale(locale.LC_TIME, "nl_NL")

PLUGIN_TITLE               = 'Nos'
BASE_URL            = 'http://nos.nl'
VIDEO_PAGE          = '%s/video-en-audio/video/pagina' % BASE_URL
JOURNAAL_BROADCAST  = '%s/video-en-audio/journaal/pagina' % BASE_URL

PAGE                = '%s/%d/%s/%s-%s-%s/'

ART                 = 'art-default.png'
ICON                = 'art-default.png'
ICON_MORE           = 'art-default.png'


####################################################################################################

def Start():
    Plugin.AddPrefixHandler('/video/nos', MainMenu, PLUGIN_TITLE, ICON, ART)
    Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
    Plugin.AddViewGroup('InfoList', viewMode='InfoList', mediaType='items')

    ObjectContainer.title1 = PLUGIN_TITLE
    ObjectContainer.art = R(ART)
    ObjectContainer.view_group = 'InfoList'
    DirectoryObject.thumb = R(ICON)
    VideoClipObject.thumb = R(ICON)

    HTTP.CacheTime = 300
    HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/536.26.17 (KHTML, like Gecko) Version/6.0.2 Safari/536.26.17'
    HTTP.Headers['Cookie'] = 'site_cookie_consent=yes'


####################################################################################################
def MainMenu():

    oc = ObjectContainer()

    oc.add(DirectoryObject(key=Callback(VideosNOS, title='Alle videos van vandaag', url=VIDEO_PAGE, urlcode=1), title='Alle videos van vandaag'))
    oc.add(DirectoryObject(key=Callback(VideosNOS, title='Laatste videos', url=BASE_URL + '/video-en-audio', urlcode=0), title='Laatste videos'))
    oc.add(DirectoryObject(key=Callback(VideosNOS, title='Meest bekeken videos van vandaag', url=VIDEO_PAGE, urlcode=2), title='Meest bekeken videos van vandaag'))
    oc.add(DirectoryObject(key=Callback(VideosNOS, title='Meest bekeken deze week', url=VIDEO_PAGE, urlcode=3), title='Meest bekeken deze week'))
    oc.add(DirectoryObject(key=Callback(VideosNOS, title='Journaaluitzendingen van vanaag', url=JOURNAAL_BROADCAST, urlcode = 1), title='Journaaluitzendingen van vanaag'))
    
    return oc

####################################################################################################

def DateUrl(url, page=1):
    now = Datetime.Now()
    finalUrl = PAGE % (
        url,
        page,
        'datum',
        now.strftime('%Y'),
        now.strftime('%m'),
        now.strftime('%d'),
        )
    return finalUrl

def VideosPupulairDay(url, page=1):
    return DateUrl(url) + 'populair/dag/'


def VideosPupulairWeek(url, page=1):
    return DateUrl(url) + 'populair/week/'

def jsonUrl(part_url):
    if ('nieuwsuur' in part_url) or ('koningshuis' in part_url):
        split_url = part_url.split('/video/')
        split_url = split_url[1].split('-')
        video_id = split_url[0]        
    elif 'uitzendingen' in part_url:
        split_url = part_url.split('/uitzendingen/')
        split_url = split_url[1].split('-')
        video_id = split_url[0]
        return JSON.ObjectFromURL("http://nos.nl/playlist/uitzending/mp4-web03/"+video_id+".json")
    else:
        split_url = part_url.split('/video/')
        split_url = split_url[1].split('-')
        video_id = split_url[0]
    return JSON.ObjectFromURL("http://nos.nl/playlist/video/mp4-web03/"+video_id+".json")

####################################################################################################

def VideosNOS(title, url, page=1, urlcode=0):

    if urlcode == 0:
        finalUrl = url
    elif urlcode == 1:
        finalUrl = DateUrl(url, page)
    elif urlcode == 2:
        finalUrl = VideosPupulairDay(url, page)
    elif urlcode == 3:
        finalUrl = VideosPupulairWeek(url, page)
    
    # dir = MediaContainer(viewGroup='List', title2=sender.itemTitle)
    oc = ObjectContainer(title2=title)
    now = Datetime.Now()
    content = HTML.ElementFromURL(finalUrl)

    Log.Debug('Start loop:')

  # Log.Debug(len(content.xpath('//ul[@class="img-list equalheight clearfix"]/li')))

    for video in content.xpath('//ul[@class="img-list equalheight clearfix"]/li'):
        
        part_url = video.xpath('./a')[0].get('href')

        if not 'nieuwsuur' in part_url:
            page_url = BASE_URL+part_url
        else:
            page_url = part_url

        json_return = jsonUrl(part_url)        
        video_title = json_return['title']
        # video_summary = json_return['description']
        # video_thumb = json_return['image']
        # video_url = json_return['videofile']
                
        #open second page, for full datetime
        getDate = HTML.ElementFromURL(page_url)
        date = getDate.xpath('//ul[@class="meta clearfix"]/li')[0].text
        video_date = Datetime.ParseDate(date, '%A %d %B %Y, %H:%M')
        
        # debugg lines
        Log.Debug('--------------------video info-------------------------')
        Log.Debug('Log Messages:')
        Log.Debug(part_url)
        Log.Debug(video_title)
        # Log.Debug(video_summary)
        # Log.Debug(video_url)
        Log.Debug(video_date)
        # Log.Debug(video_thumb)
        Log.Debug("page_url - " + page_url)

        oc.add(VideoClipObject(url=page_url, title=video_title, originally_available_at=video_date ))
        # oc.add(VideoClipObject(url=page_url, title=video_title, summary=video_summary, originally_available_at=video_date, thumb=Callback(GetThumb, url=video_thumb)))
    if len(oc) == 0:
        return MessageContainer('Geen video\'s', 'Deze directory bevat geen video\'s')
    else:
        if len(content.xpath('//div[@id="paging"]')) > 0:
            oc.add(DirectoryObject(key=Callback(VideosNOS, title='videos', url=url, page=page + 1, urlcode=urlcode), title='Meer ...', thumb=R(ICON_MORE)))
        return oc


####################################################################################################

def GetThumb(url):
    try:
        image = HTTP.Request(url, cacheTime=CACHE_1WEEK).content
        return DataObject(image, 'image/jpeg')
    except:
        return Redirect(R(ICON))
