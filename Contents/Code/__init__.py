#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

TITLE = 'Nos'
BASE_URL = 'http://nos.nl'
VIDEO_PAGE = '%s/video-en-audio/video/pagina' % BASE_URL
JOURNAAL_BROADCAST = '%s/video-en-audio/journaal/pagina' % BASE_URL

PAGE = '%s/%d/%s/%s-%s-%s/'

ART = 'art-default.png'
ICON = 'art-default.png'
ICON_MORE = 'art-default.png'


####################################################################################################

def Start():
    Plugin.AddPrefixHandler('/video/nos', MainMenu, TITLE, ICON, ART)
    Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
    Plugin.AddViewGroup('InfoList', viewMode='InfoList', mediaType='items')

    ObjectContainer.title1 = TITLE
    ObjectContainer.art = R(ART)
    ObjectContainer.view_group = 'InfoList'
    DirectoryObject.thumb = R(ICON)
    VideoClipObject.thumb = R(ICON)

    HTTP.CacheTime = CACHE_1HOUR
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

    oc = ObjectContainer(title2=title)
    now = Datetime.Now()
    content = HTML.ElementFromURL(finalUrl)

    Log.Debug('Start loop:')

  # Log.Debug(len(content.xpath('//ul[@class="img-list equalheight clearfix"]/li')))

    for video in content.xpath('//ul[@class="img-list equalheight clearfix"]/li'):
        vid_url = BASE_URL + video.xpath('./a')[0].get('href')

        # some videos link to a different website -> if they go there ignore for now

        if vid_url.find('nieuwsuur') == -1:
            if vid_url.find('koningshuis') == -1:
                vid_title = video.xpath('./a')[0].text
                summary = video.xpath('normalize-space(./span[@class="cat"]/following-sibling::text()[1])')
                date = video.xpath('./em')[0].text

                split = date.split(',')
                date = split[0]
                date = Datetime.ParseDate(date, '%m %h %Y')

                thumb = video.xpath('./span[@class="img-video"]/img')[0].get('src')

                # debugg lines

                Log.Debug('------------------------------------------o---')
                Log.Debug('Log Messages:')
                Log.Debug(url)
                Log.Debug(vid_url)
                Log.Debug(vid_title)
                Log.Debug(summary)
                Log.Debug(date)
                Log.Debug(thumb)

                oc.add(VideoClipObject(url=vid_url, title=vid_title, summary=summary, originally_available_at=date, thumb=Callback(GetThumb, url=thumb)))

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
