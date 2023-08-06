import os, time

def create_sub_directory(newDir, parentDir):
  try:
      if not os.path.exists(parentDir):
          os.makedirs(parentDir)
          time.sleep(0.2)
          path = str(newDir)
          sub_directory = os.path.join(parentDir, path)
          if not os.path.exists(sub_directory):
              os.makedirs(sub_directory)
      else:
          path = str(newDir)
          sub_directory = os.path.join(parentDir, path)
          if not os.path.exists(sub_directory):
              os.makedirs(sub_directory)
  except OSError as e:
      if e.errno != 17:
        print("OSError while creating directory: " + str(e))
        print("Consider adding a delay")
        # time.sleep might help here
        raise
      pass
