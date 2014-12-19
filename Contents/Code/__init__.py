####################################################################################################
def Start():

	ObjectContainer.title1 = 'NOS'

	HTTP.CacheTime = 300
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36'
	HTTP.Headers['Cookie'] = 'npo_cc=30'

####################################################################################################
@handler('/video/nos', 'NOS')
def MainMenu():

	oc = ObjectContainer()

	oc.add(DirectoryObject(
		key = Callback(Videos, title="Laatste journaaluitzendingen", url='http://nos.nl/uitzending/nos-journaal'),
		title = "Laatste journaaluitzendingen"
	))
	oc.add(DirectoryObject(
		key = Callback(Videos, title="Nieuwsuur", url='http://nos.nl/uitzending/nieuwsuur'),
		title = "Nieuwsuur"
	))
	oc.add(DirectoryObject(
		key = Callback(Videos, title="NOS op 3", url='http://nos.nl/uitzending/nos-op-3'),
		title = "NOS op 3"
	))
	oc.add(DirectoryObject(
		key = Callback(Videos, title="NOS Jeugdjournaal", url='http://nos.nl/uitzending/nos-jeugdjournaal'),
		title = "NOS Jeugdjournaal"
	))
	oc.add(DirectoryObject(
		key = Callback(Videos, title="NOS Sportjournaal", url='http://nos.nl/uitzending/nos-sportjournaal'),
		title = "NOS Sportjournaal"
	))
	oc.add(DirectoryObject(
		key = Callback(Videos, title="NOS Studio Sport", url='http://nos.nl/uitzending/nos-studio-sport'),
		title = "NOS Studio Sport"
	))
	oc.add(DirectoryObject(
		key = Callback(Videos, title="NOS Studio Sport Eredivisie", url='http://nos.nl/uitzending/nos-studio-sport-eredivisie'),
		title = "NOS Studio Sport Eredivisie"
	))
	oc.add(DirectoryObject(
		key = Callback(Videos, title="NOS Studio Voetbal", url='http://nos.nl/uitzending/nos-studio-voetbal'),
		title = "NOS Studio Voetbal"
	))

	return oc

####################################################################################################
@route('/video/nos/videos', page=int, allow_sync=True)
def Videos(title, url, page=1):

	oc = ObjectContainer(title2=title)
	page_url = url % (page) if '%d' in url else url
	content = HTML.ElementFromURL(page_url)
	rbar = content.xpath('.//div[contains(@class, "broadcast-player__playlist")]')[0]

	for video in rbar.xpath('.//a[contains(@class, "broadcast-link")]'):

		video_url = video.xpath('./@href')[0]

		if not video_url.startswith('http://'):
			video_url = 'http://nos.nl/%s' % video_url.lstrip('/')

		video_title = video.xpath('./span[contains(@class, "broadcast-link__name")]/text()')[0].strip() + ' ' + video.xpath('./time[contains(@class, "broadcast-link__date")]/text()')[0].strip()

		oc.add(VideoClipObject(
			url = video_url,
			title = video_title,
			thumb = Resource.ContentsOfURLWithFallback(url='')
		))

	if len(oc) < 1:
		return ObjectContainer(header="Geen video's", message="Deze directory bevat geen video's")

	if len(content.xpath('//div[@id="paging"]//a[contains(text(), "Volgende")]')) > 0:

		oc.add(NextPageObject(
			key = Callback(Videos, title=title, url=url, page=page+1),
			title = 'Meer ...'
		))

	return oc
