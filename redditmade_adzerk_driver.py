#!/Users/chrisst/.virtualenvs/redditmade/bin/python

import adzerk
import requests
import image_builder
import time
import json
import traceback

# test api key
adzerk.API_KEY = '1C2FC75BA96B6A44BFA96C1AD82545272FD6'
redditmade_url = 'http://localhost:8000/api/v1/campaigns?linked=true&launched=True'
campaign_id = '140826'
advertiser_id = '70675'
priority_id = '61083'
publisher_id= '21194'

ad_type_id = {
    'rectangle': 5,
    '3x1': 8,
}

success = []
warn = []
errors = []
whitelist = ['madclownlove', 'chrisrox', 'testes']

# **** TODO_cstephens - These are the keys/ids for reddit.com only uncomment for golive! ****
# adzerk.API_KEY = ''
# campaign_id = '140812'
# advertiser_id = '44176'
# priority_id = '61020'
# publisher_id = '7589'


def download_campaign_image(image_path, img_url):
    resp = requests.get(img_url, stream=True)
    if resp.status_code > 400:
        raise Exception('Unable to get tshit image, cannot build ad.')

    with open(image_path, 'wb') as f:
        for chunk in resp.iter_content():
            f.write(chunk)
    return image_path


def create_campaign(campaign):
    if not campaign['goal']:
        warn.append("%s doesn't have a goal set." % campaign['slug'])
        return

    keywords = [campaign['subreddit']]
    if campaign['alt_subreddits']:
        keywords = keywords + campaign['alt_subreddits'].split(',')
    # TODO_cstephens - stops us from linking live subreddits. remove when we go live.
    if [x for x in keywords if x not in whitelist]:
        warn.append("%s is linked to non-test subreddits. Ignoring." % campaign['slug'])
        return

    goal = (float(campaign['goal']) * float(campaign['price_in_cents'])) / 100
    funded = float(campaign['funded'])
    metadata = '{"percent":"%f"}' % funded
    ad_text = "%d%% funded of $%d goal" % (funded*100, goal)
    custom_ads = campaign['adzerk_three_by_one_image'] or campaign['adzerk_medium_rectangle_image']
    shirt_image = None 
    keyword_string = '\n'.join(keywords)

    if campaign['product_type'] == 'shirt' and not custom_ads:
        shirt_image = download_campaign_image('campaign_art/' + campaign['slug'], campaign['img'])
    
    elif custom_ads:
        # If custom campaign, just download art directly and treat as compiled templates for now
        download_campaign_image('compiled_templates/' + campaign['slug'] + '_3x1.png',
                                campaign['adzerk_three_by_one_image'])
        download_campaign_image('compiled_templates/' + campaign['slug'] + '_med_rect.png',
                                campaign['adzerk_medium_rectangle_image'])

    # Make the flight in the adzerk api
    new_ad = adzerk.Flight.create(CampaignId=campaign_id, Name=campaign['slug'], StartDate=time.strftime("%m/%d/%Y"),
                                  Price=0.0, Impressions=100, IsUnlimited=True, PriorityId=priority_id, IsDeleted=False,
                                  IsActive=True, Keywords=keyword_string, NoEndDate=True, GoalType=2)

    # Build the 300 x 100 size ad
    if shirt_image:
        image_builder.build_3x1_ad(image_name=campaign['slug']+'_3x1.png', shirt_image=shirt_image)
    ad_3x1_path = image_builder.update_progress(image_name=campaign['slug']+'_3x1.png', text_offset=(11, 55),
                                                text=ad_text, bar_offset=(10, 76), bar_size=(155, 14), percent=funded,
                                                goal=goal)
    creative_3x1 = adzerk.Creative.create(AdvertiserId=advertiser_id, Url='http://i.imgur.com/y4EgILj.jpg',
                                          Title=ad_3x1_path, AdTypeId=ad_type_id['3x1'], Body='test_body',
                                          Alt='test_alt', IsActive=True, IsSync=False, IsDeleted=False,
                                          Metadata=metadata)
    adzerk.Creative.upload(creative_3x1.Id, ad_3x1_path)
    adzerk.CreativeFlightMap.create(new_ad.Id, CampaignId=campaign_id, SizeOverride=False,
                                    PublisherAccountId=publisher_id, IsDeleted=False, Percentage=100,
                                    Creative={'Id': creative_3x1.Id}, IsActive=True, FlightId=new_ad.Id,
                                    Impressions=1, DistributionType=1)

    # Build the 300 x 250 size ad
    if shirt_image:
        image_builder.build_rectangle_ad(campaign['slug']+'_med_rect.png', campaign['subreddit'],
                                         shirt_image=shirt_image)
    ad_rect_path = image_builder.update_progress(image_name=campaign['slug']+'_med_rect.png', text_offset=(55, 204),
                                                 text=ad_text, bar_offset=(12, 222), bar_size=(272, 14), percent=funded,
                                                 goal=goal)
    creative_rect = adzerk.Creative.create(AdvertiserId=advertiser_id, Url='http://i.imgur.com/Bt7MlwH.jpg',
                                           Title=ad_rect_path, AdTypeId=ad_type_id['rectangle'], Body='test_body',
                                           Alt='test_alt', IsActive=True, IsSync=False, IsDeleted=False,
                                           Metadata=metadata)
    adzerk.Creative.upload(creative_rect.Id, ad_rect_path)
    adzerk.CreativeFlightMap.create(new_ad.Id, CampaignId=campaign_id, SizeOverride=False,
                                    PublisherAccountId=publisher_id, IsDeleted=False, Percentage=100,
                                    Creative={'Id': creative_rect.Id}, IsActive=True, FlightId=new_ad.Id,
                                    Impressions=1, DistributionType=1)
    success.append("creating [%s]" % campaign['slug'])
    return True

#Will eventually lose flight_id and have to get the ad by campaign_slug
def update_keywords(campaign_slug, keywords, flight_id):
    # TODO_cstephens - stops us from linking live subreddits. remove when we go live.
    if [x for x in keywords if x not in whitelist]:
        warn.append("%s is linked to non-test subreddits. Not updating flight." % campaign['slug'])
        return
    ad = adzerk.Flight.get(flight_id)
    ad.Keywords = '\n'.join(keywords)
    ad.save()
    print "flight updated"


def update_campaign(campaign, ad):
    print "updating " + campaign['slug']
    goal = (float(campaign['goal']) * float(campaign['price_in_cents'])) / 100
    percent = float(campaign['funded'])
    percent = .45  # TODO_cstephens - remove when going live
    metadata = '{"percent":"%f"}' % percent
    ad_text = "%d%% funded of $%d goal" % (percent*100, goal)
    
    # subreddit targeting
    keywords = [campaign['subreddit']]
    if campaign['alt_subreddits']:
        keywords = keywords + campaign['alt_subreddits'].split(',')
    if '\n'.join(keywords) != ad.Keywords:
        update_keywords(campaign['slug'], keywords, ad.Id)

    for creative_map in ad.CreativeMaps:
        if creative_map.Creative.AdTypeId == ad_type_id['3x1']:
            ad_3x1 = creative_map.Creative
        if creative_map.Creative.AdTypeId == ad_type_id['rectangle']:
            ad_rect = creative_map.Creative

    if not ad_3x1.Metadata:
        raise("Unable to calculate current adzerk image percent completion. Cannot update images for %s"
              % campaign['slug'])

    old_percent = float(json.loads(ad_3x1.Metadata)["percent"])

    if ad_3x1 and percent > old_percent:
        ad_3x1_path = image_builder.update_progress(
            image_name=campaign['slug']+'_3x1.png', text_offset=(11, 55), text=ad_text, bar_offset=(10, 76),
            bar_size=(155, 14), percent=percent, goal=goal)
        ad_3x1.Metadata = metadata
        ad_3x1.save()
        adzerk.Creative.upload(ad_3x1.Id, ad_3x1_path)
        success.append("progress updated [%s]" % campaign['slug'])

    if ad_rect and percent > old_percent:
        ad_rect_path = image_builder.update_progress(
            image_name=campaign['slug']+'_med_rect.png', text_offset=(55, 204), text=ad_text, bar_offset=(12, 222),
            bar_size=(272, 14), percent=percent, goal=goal)
        ad_rect.Metadata = metadata
        ad_rect.save()
        adzerk.Creative.upload(ad_rect.Id, ad_rect_path)


def deactivate_campaign(ad):
    return
    creative_maps = adzerk.CreativeFlightMap.list(ad.Id)
    if (creative_maps):
        for creative_map in creative_maps:
            if creative_map.IsActive:
                creative_map.IsActive = False
                creative_map.save()

            if creative_map.Creative.IsActive:
                creative_map.Creative.IsActive = False
                creative_map.Creative.save()

    ad.IsActive = False
    ad.save()
    return True

rm_campaigns = requests.get(redditmade_url)
# map all of the active/linked reddit campaigns
reddit_data = {}
for campaign in rm_campaigns.json():
    reddit_data[campaign['slug']] = campaign


adzerk_ads = adzerk.Flight.list(campaignId=campaign_id)
# map all of the adzerk flights associated with redditmade
adzerk_data = {}
for ad in adzerk_ads:
    adzerk_data[ad.Name] = ad


# create/update/delete based on the state of the two objects
for slug, campaign in reddit_data.iteritems():
    # if campaign[''] # isLaunched TODO_cstephens!!
    # if RM=true
    if slug in adzerk_data:
        try:
            update_campaign(campaign, adzerk_data[slug])
        except:
            print "Unable to update campaign for %s" % campaign['slug']
            traceback.print_exc()
            print
            errors.append("updating [%s]" % campaign['slug'])

        del adzerk_data[slug]  # marking the ad as 'processed' effectively

    else:
        try:
            create_campaign(campaign)
        except:
            print "Unable to create campaign for %s" % campaign['slug']
            traceback.print_exc()
            print
            errors.append("creating [%s]" % campaign['slug'])

    # if RM=false && adz==true
    # elif name in adzerk_data and adzerk_data[name].IsActive
    #   deactivate_campaign()

# final loop to clean up any ads without an active redditmade campaign
stale_ads = [y for x, y in adzerk_data.iteritems() if y.IsActive]
for stale_ad in stale_ads:
    try:
        deactivate_campaign(stale_ad)
        success.append("removing [%s]" % stale_ad.Name)
    except:
        print "Unable to deactivate campaign for %s" % stale_ad.Name
        traceback.print_exc()
        print
        errors.append("updating [%s]" % stale_ad.Name)


print "----------------results------------------"
print "-----------------------------------------"
print "Successes: "
print success
print "Warns: "
print warn
print "Errors: "
print errors
