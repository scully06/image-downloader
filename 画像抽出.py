import requests
from bs4 import BeautifulSoup
from tenacity import retry, wait_fixed
import os
from PIL import Image
from fake_useragent import UserAgent
import urllib.request


class ImageValidationPipe:
    def __init__(self, output_dir: str, min_size: Tuple[int,int] = (500,500)):
        self.file_path = output_dir
        self.min_size = min_size
        self.ua = UserAgent()
        self.hedder = {"User-Agent":str(self.ua.chrome)}

    @retry(wait=wait_fixed(3))
    def download_img(self, url):
        response = requests.get(url, headers=self.header)
        soup = BeautifulSoup(response.text,"html.parser")
        for link in soup.find_all("img"):
            try:
                urlData = requests.get(link.get("src"), headers=self.hedder).content
                filename = os.path.basename(link.get("src"))
                try:
                    opener = urllib.request.build_opener()
                    opener.addheaders = [("User-Agent", "Mozilla/5.0")]
                    urllib.request.install_opener(opener)
                    url_temp = urllib.request.urlopen(link.get("src"))
                    url_temp.close()
                except Exception as h:
                    #print(h)
                    continue
                else:
                    is_broken = self.verify_download(urlData,filename)
                    self.check_img(filename,is_broken)
            except Exception as e:
                continue
    
    def verify_download(self,urlData,filename):
        with open(self.file_path + "/" + filename,"wb") as g:
            g.write(urlData)
        try:
            with Image.open(self.file_path + "/" + filename) as r:
                width ,height = r.size
                im = Image.open(r, "r")
                try:
                    im.verify()
                except Exception as q:
                    print("1")
                    print(q)
                    return True
        except Exception as j:
            print(j)
            return True
        if width <= self.min_size[0] or height <= self.min_size[1]:
            return True

    def check_img(self,filename,flag_broken):
        if flag_broken == True:
            os.remove(self.file_path + "/" + filename)             
        if os.path.exists(self.file_path + "/" + filename) == True:
            os.remove(self.file_path + "/" + filename)


                