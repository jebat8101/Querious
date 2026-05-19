from ghunt import globals as gb
from ghunt.objects.base import GHuntCreds
from ghunt.apis.peoplepa import PeoplePaHttp
from ghunt.apis.vision import VisionHttp
from ghunt.helpers import gmaps, auth, ia
from ghunt.helpers.knowledge import get_user_type_definition
from ghunt.helpers.utils import get_httpx_client

import httpx

from typing import *
from pathlib import Path


async def hunt(as_client: httpx.AsyncClient, gaia_id: str, json_file: Path=None):
    if not as_client:
        as_client = get_httpx_client()

    ghunt_creds = await auth.load_and_auth(as_client)

    #gb.rc.print("\n[+] Target found !", style="spring_green3")

    people_pa = PeoplePaHttp(ghunt_creds)
    # vision_api = VisionHttp(ghunt_creds)
    is_found, target = await people_pa.people(as_client, gaia_id, params_template="max_details")
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

    print(f"Gaia ID : {target.personId}\n")

    if container in target.profileInfos:
        print("User types :")
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

    gb.rc.print("\n🗺️ Maps data", style="green4")

    err, stats, reviews, photos = await gmaps.get_reviews(
        as_client, target.personId, cookies=ghunt_creds.cookies
    )
    gmaps.output(err, stats, reviews, photos, target.personId)

    if json_file:
        if container == "PROFILE":
            json_results[f"{container}_CONTAINER"] = {
                "profile": target,
                "maps": {
                    "photos": photos,
                    "reviews": reviews,
                    "stats": stats
                }
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