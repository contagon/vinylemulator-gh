import time
import nfc
import pychromecast
from spotify_controller import SpotifyController
import spotify_token as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from const import *

# TODO: Should be able to use the same credentials for both
# starting spotify on the chromecast and using spotify
# but I could never get it to work

def main():
    # uri = "spotify:album:02tIakRsIFGW8sO4pBtJgj"
    # play(uri)

    # Connect to NFC reader
    try:
        reader = nfc.ContactlessFrontend('usb')
    except IOError as e:
        print ("... could not connect to reader")
        return

    #wait till we're tagged
    while True:
        reader.connect(rdwr={'on-connect': touched, 'beep-on-connect': True})
        time.sleep(1)


#########################################################
#####                 READ NFC TAG                  #####
#########################################################
def touched(tag):
    """Connect to spotify, then send URI found on tag to it"""
    #send uri
    if tag.ndef:
        # Connect to google device and spotify
        for record in tag.ndef.records:
            uri = record.text
            play(uri)

    return True

#########################################################
#####             PLAY A SPECIFIC URI               #####
#########################################################
def play(uri):
    client, device = connect()

    #if it's a track just play it
    if "track" in uri:
        client.start_playback(device_id=device, uris=[uri])
    #if it's an album/artist/playlist
    else:
        client.start_playback(device_id=device, context_uri=uri)


#########################################################
#####            CONNECT TO GH & SPOTIFY            #####
#########################################################
def connect():
    # Connect to the chromecast
    cast = pychromecast.Chromecast(ip)
    cast.wait()

    # Launch spotify app on the chromecast
    data = st.start_session(sp_dc, sp_key)
    access_token = data[0]
    expires = data[1] - int(time.time())
    sp = SpotifyController(access_token, expires)
    cast.register_handler(sp)
    sp.launch_app()

    # Check what devices are available now
    auth = SpotifyOAuth(scope=scope,
                    client_id=client_id,
                    client_secret=client_secret,
                    redirect_uri=redirect_uri,
                    cache_path="/home/pi/vinylemulator-gh/.spotify.txt")
    client = spotipy.Spotify(auth_manager=auth)
    devices_available = client.devices()

    # Match active spotify devices with the spotify controller's device id
    spotify_device_id = [d["id"] for d in devices_available["devices"] if d["id"] == sp.device][0]

    return client, spotify_device_id


if __name__ == "__main__":
    main()
