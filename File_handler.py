from Downloader import Downloader
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import os 
import polars as pl

WORKERS = 10
FILES = 100
    ## Reads URLs from the Excel file, manages the download process, and writes the log of downloaded files.
class FileHandler:
    def __init__(self, file_path_gri, destination_folder, output_folder):
        self.file_path_gri = file_path_gri
        self.downloader = Downloader(destination_folder)
        self.success_list = []
        self.output_folder = output_folder
    
    def start_download(self):
    # Indlæser URL fra GRI filen.
        df = pl.read_excel(self.file_path_gri, columns=["BRnum", "Pdf_URL", "Report Html Address"])
    #Test
        print(df.head())  # Her printer jeg nogle rows, det var til debugging, men lod den være for at visualisere data. 
        urls = []
        count = 0
        for row in df.rows(named=True):
            #Her laver jeg et break, hvis jeg er over x-antal filer. 
            if count == FILES:
                break
            primary_url = row['Pdf_URL']
            secondary_url = row['Report Html Address']
            filename = f"{row['BRnum']}.pdf"
            count += 1
            #Appender URL'erne til arrayet. Enten primært eller sekundært.
            if primary_url:
                urls.append((primary_url, filename))
            else: 
                urls.append((secondary_url, filename)) 
        
        log_list = []
        # Tråd initialisering
        with ThreadPoolExecutor(max_workers=WORKERS) as executor:  
            # Her opretter jeg en dict, hvor nøglen er en "future", det repræsentere en opg½ave som skal løses, og værdien er tuples med URL og filename.
            future_to_url = {executor.submit(self.downloader.download, url, filename): (url, filename) for url, filename in urls}
            # as_completed returnere futures når de er færdiggjort. 
            for future in as_completed(future_to_url):
                url, filename = future_to_url[future]
                try:
                    # .result() metoden blokerer, indtil futuren/opgaven er færdig, og vi får en success/bool tilbage 
                    success = future.result()
                    log_list.append({"BRNum": filename.split('.')[0], "Download_Status": 'Downloadet' if success else 'Ikke downloadet'})
                except Exception as exc:
                    # .result() sender en exception hvis der opstod fejl under downloda.
                    print(f"Error downloading {url}: {exc}")
                    log_list.append({"BRNum": filename.split('.')[0], "Download_Status": 'Ikke downloadet'})
        # Når opgaven er helt færdig, og alle trådene er kørt igennem, skriver jeg til log filen. 
        self.write_downloaded_files(log_list)
        
    def write_downloaded_files(self, log_list):
        # Først sortere jeg listen, da vi bruger tråde der bliver færdige på forskellige tidspunkter, kommer de først ind relativt tilfældigt. 
        # Man kan løse problemet ved, at vente på hver tråd, men så ryger pointen i trådning.
        sorted_log_list = sorted(log_list, key=lambda x: x["BRNum"])
        # Her indlæser vi listen fra metoden før, der er et BRNum til hver fil og en "downloadet/ikke downloadet" string.
        output_path = os.path.join(self.output_folder, "downloaded_files.xlsx")
        df = pd.DataFrame(sorted_log_list)
        # Gemmer osv... 
        df.to_excel(output_path, index=False)
        print(f"List of downloaded files written to {output_path}")