#!/Users/chrisst/.virtualenvs/redditmade/bin/python

import adzerk
import requests
import image_builder

adzerk.API_KEY = '1C2FC75BA96B6A44BFA96C1AD82545272FD6'
campaign_id = '140826'
advertiser_id = '70675'

#### TODO - These are the keys/ids for reddit.com only uncomment for golive!
#adzerk.API_KEY = '205261CFA833AA4270AB2C2A73AF44034880' # REDDIT FO REAL
#campaign_id = 
#advertiser_id = ''

def create_campaign(campaign):
    print "omg making a new campaign!"
    print campaign
    goal = (float(campaign['goal']) * float(campaign['price_in_cents'])) / 100
    funded = float(campaign['funded'])
    percent = (funded / goal)

    print "goal is %d" % goal
    image_builder.build_3x1_ad(funded, goal)

def update_campaign(campaign, ad):
    print "omg updating campaign!"
    return True
    #create new image

def deactivate_campaign(ad):
    print "omg deleting campaign!"
    print ad.Id, ad.Name
    return # TODO remove soon
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


rm_campaigns = requests.get('http://localhost:8000/api/v1/campaigns?linked=true')
#map all of the active/linked reddit campaigns
reddit_data = {}
for campaign in rm_campaigns.json():
    print campaign['slug']
    #TODO - throw exception if already exists
    reddit_data[campaign['slug']] = campaign;


adzerk_ads = adzerk.Flight.list(campaignId=campaign_id)
#map all of the adzerk flights associated with redditmade
adzerk_data = {}
for ad in adzerk_ads:
    print ad.Name
    #TODO - throw exception if already exists
    adzerk_data[ad.Name] = ad


# create/update/delete based on the state of the two objects
for slug, campaign in reddit_data.iteritems():
    print
    print slug
    #if campaign[''] # isLaunched TODO!!

    #if RM=true 
    if slug in adzerk_data:
        if update_campaign(campaign, adzerk_data[slug]):
            del adzerk_data[slug] #marking the ad as 'processed' effectively

    else:
        create_campaign(campaign)

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

