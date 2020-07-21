import time
import nfc
import pychromecast
from pychromecast.controllers.spotify import SpotifyController
import spotify_token as st
import spotipy

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

#########################################################
#####            CONFIGURATION VARIABLES            #####
#########################################################
ip     = "192.168.0.9"
sp_dc  = ""
sp_key = ""

def main():
    # Connect to NFC reader
    try:
        reader = nfc.ContactlessFrontend('usb')
    except IOError as e:
        print ("... could not connect to reader")

    #wait till we're tagged
    while True:
        reader.connect(rdwr={'on-connect': touched, 'beep-on-connect': True})
        time.sleep(0.1)


#########################################################
#####              CONNECT TO SERVICES              #####
#########################################################
def connect():
    """Used to activate spotify application on google home, then find that device in spotify"""
    # Wait for connection to the chromecast
    cast = pychromecast.Chromecast(ip)
    cast.wait()

    # Create a spotify token
    data = st.start_session(sp_dc, sp_key)
    access_token = data[0]
    expires = data[1] - int(time.time())

    # Launch the spotify app on the cast we want to cast to
    sp = SpotifyController(access_token, expires)
    cast.register_handler(sp)
    sp.launch_app()

    # Query spotify for active devices
    client = spotipy.Spotify(auth=access_token)
    devices_available = client.devices()

    # Match active spotify devices with the spotify controller's device id
    for device in devices_available["devices"]:
        if device["id"] == sp.device:
            spotify_device_id = device["id"]
            break

    return client, spotify_device_id


#########################################################
#####                 READ NFC TAG                  #####
#########################################################
def touched(tag):
    """Connect to spotify, then send URI found on tag to it"""

    #send uri
    if tag.ndef:
        # Connect to google device and spotify
        client, device = connect()

        for record in tag.ndef.records:
            uri = record.text
            # uri = "spotify:album:02tIakRsIFGW8sO4pBtJgj"

            print("Read from NFC tag: "+ uri)

            #if it's a track just play it
            if "track" in uri:
                client.start_playback(device_id=device, uris=[uri])
            #if it's an album/artist/playlist
            else:
                client.start_playback(device_id=device, context_uri=uri)

    return True

if __name__ == "__main__":
    main()