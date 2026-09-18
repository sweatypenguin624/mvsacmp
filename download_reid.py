from ultralytics.utils.downloads import attempt_download_asset
import shutil
import os

filepath = attempt_download_asset('osnet_x0_25_msmt17.pt')
print("Downloaded to:", filepath)
if str(filepath) != os.path.abspath('osnet_x0_25_msmt17.pt'):
    shutil.copy(filepath, 'osnet_x0_25_msmt17.pt')
    print("Copied to current directory")
