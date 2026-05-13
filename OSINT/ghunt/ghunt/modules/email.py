from ghunt import globals as gb
from ghunt.helpers.utils import get_httpx_client
from ghunt.objects.base import GHuntCreds
from ghunt.apis.peoplepa import PeoplePaHttp
from ghunt.apis.vision import VisionHttp
from ghunt.helpers import gmaps, playgames, auth, calendar as gcalendar, ia
from ghunt.helpers.knowledge import get_user_type_definition

import httpx

from typing import *
from pathlib import Path


async def hunt(as_client: httpx.AsyncClient, email_address: str, json_file: Path=None):
    if not as_client:
        as_client = get_httpx_client()
 
    ghunt_creds = await auth.load_and_auth(as_client)

    #gb.rc.print("[+] Target found !", style="sea_green3")

    people_pa = PeoplePaHttp(ghunt_creds)
    # vision_api = VisionHttp(ghunt_creds)
    is_found, target = await people_pa.people_lookup(as_client, email_address, params_template="max_details")
    if not is_found:
        exit("[-] The target wasn't found.")

    if json_file:
        json_results = {}

    containers = target.sourceIds

    if len(containers) > 1 or not "PROFILE" in containers:
        print("[!] You have this person in these containers :")
        for container in containers:
            print(f"- {container.title()}")

    if not "PROFILE" in containers:
        exit("[-] Given information does not match a public Google Account.")

    container = "PROFILE"
    
    gb.rc.print("🙋 Google Account data\n", style="plum2")

    if container in target.names and (
        getattr(target.names[container], "fullname", None)
        or getattr(target.names[container], "firstName", None)
    ):
        n = target.names[container]
        parts = [p for p in (n.fullname, n.firstName, n.lastName) if p]
        if parts:
            print(f"Name : {' '.join(parts)}\n")

    gaia = target.personId
    gb.rc.print("[Links]", style="bold")
    print(f"Maps contributor : https://www.google.com/maps/contrib/{gaia}/reviews")
    print(f"Photos (if public) : https://www.google.com/maps/contrib/{gaia}/photos")
    print()

    if container in target.profilePhotos:
        if target.profilePhotos[container].isDefault:
            print("[-] Default profile picture")
        else:
            print("[+] Custom profile picture !")
            print(f"=> {target.profilePhotos[container].url}")
            
            # await ia.detect_face(vision_api, as_client, target.profilePhotos[container].url)
            print()

    if container in target.coverPhotos:
        if target.coverPhotos[container].isDefault:
            print("[-] Default cover picture\n")
        else:
            print("[+] Custom cover picture !")
            print(f"=> {target.coverPhotos[container].url}")

            # await ia.detect_face(vision_api, as_client, target.coverPhotos[container].url)
            print()

    _lu = target.sourceIds[container].lastUpdated
    if _lu:
        print(f"Last profile edit : {_lu.strftime('%Y/%m/%d %H:%M:%S (UTC)')}\n")
    else:
        print("Last profile edit : (not provided by API)\n")
    
    if container in target.emails:
        print(f"Email : {target.emails[container].value}")
    else:
        print(f"Email : {email_address}\n")

    print(f"Gaia ID : {target.personId}")

    if container in target.profileInfos:
        print("\nUser types :")
        for user_type in target.profileInfos[container].userTypes:
            definition = get_user_type_definition(user_type)
            gb.rc.print(f"- {user_type} [italic]({definition})[/italic]")

    gb.rc.print(f"\n📞 Google Chat Extended Data\n", style="light_salmon3")

    dd = target.extendedData.dynamiteData
    if dd.presence:
        print(f"Presence : {dd.presence}")
    print(f"Entity Type : {dd.entityType}")
    if dd.dndState:
        print(f"DND State : {dd.dndState}")
    gb.rc.print(f"Customer ID : {x if (x := dd.customerId) else '[italic]Not found.[/italic]'}")

    gb.rc.print(f"\n🌐 Google Plus Extended Data\n", style="cyan")

    print(f"Entreprise User : {target.extendedData.gplusData.isEntrepriseUser}")
    cr = target.extendedData.gplusData.contentRestriction
    if cr:
        print(f"Content Restriction : {cr}")
    
    if container in target.inAppReachability:
        print("\n[+] Activated Google services :")
        for app in target.inAppReachability[container].apps:
            print(f"- {app}")

    gb.rc.print("\n🎮 Play Games data", style="deep_pink2")

    player = None
    player_results = await playgames.search_player(ghunt_creds, as_client, email_address)
    if player_results:
        if len(player_results) > 1:
            print(f"\n[!] {len(player_results)} Play Games search matches (using the first):")
            for i, cand in enumerate(player_results[:10], 1):
                print(f"  {i}. {cand.name} — id={cand.id}")
            if len(player_results) > 10:
                print(f"  ... and {len(player_results) - 10} more.")
        player_candidate = player_results[0]
        print("\n[+] Found player profile !")
        print(f"\nUsername : {player_candidate.name}")
        print(f"Player ID : {player_candidate.id}")
        print(f"Avatar : {player_candidate.avatar_url}")
        print(f"Profile URL : https://play.google.com/games/profile/{player_candidate.id}")
        _, player = await playgames.get_player(ghunt_creds, as_client, player_candidate.id)
        playgames.output(player)
    else:
        print("\n[-] No player profile found.")

    gb.rc.print("\n🗺️ Maps data", style="green4")

    err, stats, reviews, photos = await gmaps.get_reviews(as_client, target.personId)
    gmaps.output(err, stats, reviews, photos, target.personId)

    gb.rc.print("\n🗓️ Calendar data\n", style="slate_blue3")

    cal_found, calendar, calendar_events = await gcalendar.fetch_all(ghunt_creds, as_client, email_address)

    if cal_found:
        print("[+] Public Google Calendar found !\n")
        if calendar_events.items:
            cal_name = ""
            if container in target.names:
                cal_name = target.names[container].fullname or ""
            gcalendar.out(calendar, calendar_events, email_address, cal_name, limit=25)
        else:
            print("=> No recent events found.")
    else:
        print("[-] No public Google Calendar.")

    if json_file:
        if container == "PROFILE":
            json_results[f"{container}_CONTAINER"] = {
                "profile": target,
                "play_games": player if (player_results and player is not None) else None,
                "maps": {
                    "photos": photos,
                    "reviews": reviews,
                    "stats": stats
                },
                "calendar": {
                    "details": calendar,
                    "events": calendar_events
                } if cal_found else None
            }
        else:
            json_results[f"{container}_CONTAINER"] = {
                "profile": target
            }

    if json_file:
        import json
        from ghunt.objects.encoders import GHuntEncoder;
        with open(json_file, "w", encoding="utf-8") as f:
            f.write(json.dumps(json_results, cls=GHuntEncoder, indent=4))
        gb.rc.print(f"\n[+] JSON output wrote to {json_file} !", style="italic")

    await as_client.aclose()