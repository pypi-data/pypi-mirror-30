from .aiodisk import main
from .googledrive import GoogleDrive

if __name__ == '__main__':
    if GoogleDrive.isSetupValid():
        main()
    else:
        GoogleDrive.getCredientials()
