import os 
import requests
## Handles individual PDF downloads
class Downloader:
    def __init__(self, destination_folder):
        self.destination_folder = destination_folder

    def download(self, url, destination_filename):
        try:
            # Jeg får en del fejl med, at hjemmesidernes SSL certifikat er udløbet. 
            # Man kan sætte en verify param på requesten, som gør man ignorere den.
            # Jeg har valgt at undlade det, da det kan være usikkert. 
            response = requests.get(url, timeout=50) # Den stopper med at forsøge efter timeout sekunder.  
            
            # Tjekker om filen er en PDF, da det står i krav specifikationen. 
            if not "application/pdf" in response.headers.get("content-type"):
                raise Exception("Not PDF type")
            if response.status_code == 200: # Hvis requesten var successfuld
                # Gemmer filen
                os.makedirs(self.destination_folder, exist_ok=True)  
                with open(os.path.join(self.destination_folder, destination_filename), 'wb') as file:
                    file.write(response.content)
                # Printer til brugeren at det lykkedes (Kan udkommenteres for spam)
                print(f"Download successful: {destination_filename}")
                return True
            else:
                # Fejlbesked
                print(f"Failed to download: {destination_filename} with status code: {response.status_code}")
                return False
        except requests.RequestException as e:
            print(f"Error downloading {url}: {e}")
            return False