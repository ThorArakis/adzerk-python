#!/Users/chrisst/.virtualenvs/redditmade/bin/python

import adzerk
import requests
import image_builder
import time

import sys

adzerk.API_KEY = '1C2FC75BA96B6A44BFA96C1AD82545272FD6'
redditmade_url = 'http://localhost:8000/api/v1/campaigns?linked=true&launched=True'
campaign_id = '140826'
advertiser_id = '70675'
priority_id = '61083'
publisher_id= '21194'

ad_type_id = {
    'rectangle':5,
    '3x1':8,
}

#### TODO - These are the keys/ids for reddit.com only uncomment for golive!
#adzerk.API_KEY = '' # REDDIT FO REAL
# campaign_id = ''
# advertiser_id = '44176'
# priority_id = '61020'
# publisher_id= '7589'

def create_campaign(campaign):
    print "omg making a new campaign!"
    #print campaign
    goal = (float(campaign['goal']) * float(campaign['price_in_cents'])) / 100
    funded = float(campaign['funded'])
    metadata="{'percent':'%d'}" % funded
    ad_text = "%d%% funded of $%d goal" % (funded*100, goal)

    ad_3x1_path = image_builder.build_3x1_ad(campaign['slug']+'_3x1.png')
    image_builder.update_progress(campaign['slug']+'_3x1.png', (11, 55), ad_text, (10,76), (155,14), funded)
    image_builder.update_progress(image_name=campaign['slug']+'_3x1.png', text_offset=(11, 55), text=ad_text, 
                                  bar_offset=(10,76), bar_size=(155,14), percent=funded, goal=goal)

    ad_rect_path = image_builder.build_rectangle_ad(campaign['slug']+'_med_rect.png', campaign['subreddit'])
    image_builder.update_progress(image_name=campaign['slug']+'_med_rect.png', text_offset=(55, 204), text=ad_text, 
                                  bar_offset=(12,222), bar_size=(272,14), percent=funded, goal=goal)

    print "creating and uploading ad"
    creative_3x1 = adzerk.Creative.create(AdvertiserId=advertiser_id, Url='http://i.imgur.com/y4EgILj.jpg', 
                                          Title=ad_3x1_path, AdTypeId=ad_type_id['3x1'], Body='test_body', 
                                          Alt='test_alt', IsActive=True, IsSync=False, IsDeleted=False, 
                                          Metadata=metadata)
    adzerk.Creative.upload(creative_3x1.Id, ad_3x1_path)

    creative_rect = adzerk.Creative.create(AdvertiserId=advertiser_id, Url='http://i.imgur.com/Bt7MlwH.jpg', 
                                           Title=ad_rect_path, AdTypeId=ad_type_id['rectangle'], Body='test_body', 
                                           Alt='test_alt', IsActive=True, IsSync=False, IsDeleted=False, 
                                           Metadata=metadata)
    adzerk.Creative.upload(creative_rect.Id, ad_rect_path)

    print "making the flight!"
    new_ad = adzerk.Flight.create(CampaignId=campaign_id, Name=campaign['slug'], StartDate=time.strftime("%m/%d/%Y"), 
                                  Price=0.0, Impressions=1, IsUnlimited=True, PriorityId=priority_id, IsDeleted=False, 
                                  IsActive=True, Keywords=campaign['subreddit'] )
    print new_ad

    print "making flight maps"
    ad_map = adzerk.CreativeFlightMap.create(new_ad.Id, CampaignId=campaign_id, SizeOverride=False,
                                            PublisherAccountId=publisher_id, IsDeleted=False, Percentage=100, 
                                            Creative={'Id':creative_3x1.Id}, IsActive=True, FlightId=new_ad.Id, 
                                            Impressions=1, DistributionType=1)
    print ad_map
    ad_map2 = adzerk.CreativeFlightMap.create(new_ad.Id, CampaignId=campaign_id, SizeOverride=False, 
                                              PublisherAccountId=publisher_id, IsDeleted=False, Percentage=100, 
                                              Creative={'Id':creative_rect.Id}, IsActive=True, FlightId=new_ad.Id, 
                                              Impressions=1, DistributionType=1)
    print ad_map2

def update_campaign(campaign, ad):
    print "omg updating campaign!"
    # adzerk.Flight.get()
    #TODO activate the flight, as there isn't a unique constraint for flight name
    return True
    #create new image

def deactivate_campaign(ad):
    print "omg deleting campaign!"
    print ad.Id, ad.Name
    creative_maps = adzerk.CreativeFlightMap.list(ad.Id)
    if (creative_maps):
        for creative_map in creative_maps:
            if creative_map.IsActive:
                print "Deactivating creative map: %d" % creative_map.Id
                creative_map.IsActive = False
                creative_map.save()
            if creative_map.Creative.IsActive:
                print "Deactivating creative: %d" % creative_map.Creative.Id
                creative_map.Creative.IsActive = False
                creative_map.Creative.save()
    
    print "Deactivating ad: %d" % ad.Id
    ad.IsActive = False
    ad.save()
    print "huzzah"
    return True


rm_campaigns = requests.get(redditmade_url)
#map all of the active/linked reddit campaigns
reddit_data = {}
for campaign in rm_campaigns.json():
    # print campaign['slug']
    #TODO - throw exception if already exists
    reddit_data[campaign['slug']] = campaign;


adzerk_ads = adzerk.Flight.list(campaignId=campaign_id)
#map all of the adzerk flights associated with redditmade
adzerk_data = {}
for ad in adzerk_ads:
    # print ad.Name
    #TODO - throw exception if already exists
    adzerk_data[ad.Name] = ad


# create/update/delete based on the state of the two objects
for slug, campaign in reddit_data.iteritems():
    print
    print "Evaluating redditmade campaign: %s" % slug
    #if campaign[''] # isLaunched TODO!!

    #if RM=true 
    if slug in adzerk_data:
        try:
            if update_campaign(campaign, adzerk_data[slug]):
                del adzerk_data[slug] #marking the ad as 'processed' effectively
        except:
            print "Unable to create campaign for %s" % campaign['slug']

    else:
        try:
            create_campaign(campaign)
        except:
            print "Unable to create campaign for %s" % campaign['slug']

    #if RM=false && adz==true
    #elif name in adzerk_data and adzerk_data[name].IsActive
    #   deactivate_campaign()

print
print "----------------cleanup------------------"
print "-----------------------------------------" 
# final loop to clean up any ads without an active redditmade campaign
stale_ads = [y for x,y in adzerk_data.iteritems() if y.IsActive]
print "things to delete"
for stale_ad in stale_ads:
    print stale_ad
    deactivate_campaign(stale_ad)

