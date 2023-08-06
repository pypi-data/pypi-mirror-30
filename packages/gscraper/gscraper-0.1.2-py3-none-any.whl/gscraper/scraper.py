import time, ssl

from urllib.request import urlopen, URLError, HTTPError

from .web import generateWebRequest

def get_next_image_url_from_html( htmlString ):

  s = htmlString

  # class existing on all image containers in the search results
  img_identifier = s.find('rg_di')

  if img_identifier >= 0:
    # extract url for full image
    meta_data_start = s.find('"class="rg_meta"')
    img_url_start = s.find('"ou"', meta_data_start + 1)
    remaining_html = s.find(',"ow"', img_url_start + 1)
    img_url = str(s[img_url_start + 6:remaining_html - 1])

    return img_url, remaining_html

  return "no_links", 0

def get_all_imgage_urls_from_html( htmlString, limit=-1 ):

  # hard limit; only ~100 images are displayed per image search
  limit = 100 if int(limit) < 0 else int(limit)

  img_urls = []

  while len(img_urls) < limit:
    img_url, remaining_html = get_next_image_url_from_html(htmlString)

    if img_url == "no_links":
      break
    else:
      img_urls.append(img_url)
      time.sleep(0.1)
      htmlString = htmlString[remaining_html:]

  return img_urls

def download_images( imgURLs, target_directory = "downloads", delay = 0, start_index = 0 ):

  errorCount = 0

  for i in range(len(imgURLs)):
    imgURL = imgURLs[i]

    try:
        image_name = str(imgURL[(imgURL.rfind('/')) + 1:]).lower()

        if ".jpg" in image_name:
          file_extension = ".jpg"

        elif ".png" in image_name:
          file_extension = ".png"

        elif ".jpeg" in image_name:
          file_extension = ".jpeg"

        elif ".svg" in image_name:
          file_extension = ".svg"

        else:
          file_extension = ".jpg"

        # current image number
        i_with_leading_zeros = ("{:0"+str(len(str(len(imgURLs))))+"}").format(start_index + i + 1)

        file_name = "image-" + i_with_leading_zeros

        output_file = open(target_directory + "/" + file_name + file_extension, 'wb')

        req = generateWebRequest(imgURL)
        img = urlopen(req, None, 15).read()

        output_file.write(img)
        output_file.close()

        print("completed ====> " + str(start_index + i + 1) + ". " + image_name)

    except HTTPError as e:
        errorCount += 1
        print("HTTPError on image " + str(start_index + i + 1))
        print(str(e))

    except URLError as e:
        errorCount += 1
        print("URLError on image " + str(start_index + i + 1))
        print(str(e))

    except IOError:
        errorCount += 1
        print("IOError on image " + str(start_index + i + 1))

    except ssl.CertificateError as e:
        errorCount += 1
        print("CertificateError on image " + str(start_index + i + 1))
        print(str(e))

    if int(delay) > 0:
        time.sleep(int(delay))

  return errorCount
