####################################################################################################
def Start():

	ObjectContainer.title1 = 'NOS'

	HTTP.CacheTime = 300
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/536.26.17 (KHTML, like Gecko) Version/6.0.2 Safari/536.26.17'
	HTTP.Headers['Cookie'] = 'site_cookie_consent=yes'

####################################################################################################
@handler('/video/nos', 'NOS')
def MainMenu():

	oc = ObjectContainer(no_cache=True)

	oc.add(DirectoryObject(
		key = Callback(Videos, title="Alle video's van vandaag", url='http://nos.nl/video-en-audio/video/pagina/%%d/datum/%s' % Datetime.Now().strftime('%Y-%m-%d')),
		title = "Alle video's van vandaag"
	))
	oc.add(DirectoryObject(
		key = Callback(Videos, title="Laatste video's", url='http://nos.nl/video-en-audio'),
		title = "Laatste video's"
	))
	oc.add(DirectoryObject(
		key = Callback(Videos, title="Meest bekeken vandaag", url='http://nos.nl/video-en-audio/video/pagina/%%d/datum/%s/populair/dag/' % Datetime.Now().strftime('%Y-%m-%d')),
		title = "Meest bekeken vandaag"
	))
	oc.add(DirectoryObject(
		key = Callback(Videos, title="Meest bekeken deze week", url='http://nos.nl/video-en-audio/video/pagina/%%d/datum/%s/populair/week/' % Datetime.Now().strftime('%Y-%m-%d')),
		title = "Meest bekeken deze week"
	))
	oc.add(DirectoryObject(
		key = Callback(Videos, title="Journaaluitzendingen van vandaag", url='http://nos.nl/video-en-audio/journaal/pagina/%%d/datum/%s/' % Datetime.Now().strftime('%Y-%m-%d')),
		title = "Journaaluitzendingen van vandaag"
	))

	return oc

####################################################################################################
@route('/video/nos/videos', page=int, allow_sync=True)
def Videos(title, url, page=1):

	oc = ObjectContainer(title2=title)
	page_url = url % page if '%d' in url else url
	content = HTML.ElementFromURL(page_url)

	for video in content.xpath('//ul[contains(@class, "img-list")]/li'):
		video_url = video.xpath('./a/@href')[0]

		if not video_url.startswith('http://'):
			video_url = 'http://nos.nl/%s' % video_url.lstrip('/')

		video_title = video.xpath('./a/text()')[0].strip()
		summary = video.xpath('./span[@class="cat"]/following-sibling::text()')[0].strip()
		thumb = video.xpath('.//img/@src')[0].replace('/xs/', '/xl/')
		date = video.xpath('./em/text()')[-1].split(',')[0].replace('mrt', 'mar').replace('mei', 'may').replace('okt', 'oct')
		date = Datetime.ParseDate(date).date()

		oc.add(VideoClipObject(
			url = video_url,
			title = video_title,
			summary = summary,
			thumb = Resource.ContentsOfURLWithFallback(thumb),
			originally_available_at = date
		))

	if len(oc) < 1:
		return ObjectContainer(header="Geen video's", message="Deze directory bevat geen video's")

	if len(content.xpath('//div[@id="paging"]//a[contains(text(), "Volgende")]')) > 0:
		oc.add(NextPageObject(
			key = Callback(Videos, title=title, url=url, page=page+1),
			title = 'Meer ...'
		))

	return oc
