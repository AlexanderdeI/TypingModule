from datetime import date

PROJECT_PATH = 'Z:\!Cemeteries\_QGIS'
PHOTO_POSITION = 'LEFT' # RIGHT или LEFT
MAX_PHOTO_ZOOM = 15
ZOOM_RATIO = 1.2
BASE_ZOOM = 1
MIN_ZOOM = 0.15

GPKG_LAYER_NAME = 'graves'

AUTOSAVE_TIME = 10.0
AUTOCOMPLETE_CENTURY = 20
MIN_YEAR = 1700
MAX_AGE = 130
TODAY = date.today()

# Имена полей
SURNAME = 'surname'
NAME = 'name'
MIDDLENAME = 'middlename'
BIRTH = 'birth'
DEATH = 'death'
GRAVETYPE = 'gravetype'
CONDITION = 'condition'
SECTOR = 'sector'
ROW = 'row'
LAND = 'land'
PLACE = 'place'
UCODE = 'ucode'
ADDRESS = 'address'
COMMENT = 'comment'
PHOTO = 'photo'
PHOTO2 = 'photo2'