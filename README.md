# Avito Cars

Script that parses cars on avito.ru. This script is working with PostgeSQL database.

### Description
`classes.py` contains classes of car objects and SQLModel  
`config.txt` contains CSS tags that may be changed in the future  
`df_to_db.py` contains functions that convert csv files into dataframe and send them to the database  
`main.py` main executable script  
`research.ipynb` research notebook with some analysis scripts (may be deleted)  
`shared.py` containes variables that are shared between functions  

 ### Configuring the script
 1. Car objects should be configured manually in the `shared.py/cars_dict` variable
 3. This app is ready for containerization.
 4. Table `logger` contains some logging information.