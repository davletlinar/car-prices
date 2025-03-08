from datetime import date


total_time = 0
elapsed_time = 0
page_counter = 0
http_errors_counter = 0
total_pages = 0
PUBDATE = date.today().strftime("%Y-%m-%d")

logo = '''
 a88888b.                       888888ba           oo                            
d8'   `88                       88    `8b                                        
88        .d8888b. 88d888b.    a88aaaa8P' 88d888b. dP .d8888b. .d8888b. .d8888b. 
88        88'  `88 88'  `88     88        88'  `88 88 88'  `"" 88ooood8 Y8ooooo. 
Y8.   .88 88.  .88 88           88        88       88 88.  ... 88.  ...       88 
 Y88888P' `88888P8 dP           dP        dP       dP `88888P' `88888P' `88888P'
        '''
        
cars_dict = {
        "volkswagen": [
            "amarok",
            "arteon",
            "golf",
            "jetta",
            "passat",
            "passat_cc",
            "polo",
            "teramont",
            "tiguan",
            "touareg"
        ],
        "audi": [
            "a1",
            "a3",
            "a4",
            "a5",
            "a6",
            "a7",
            "a8",
            "q3",
            "q5",
            "q6",
            "q7",
            "q8",
            "tt"
        ],
        "skoda": [
            "fabia",
            "karoq",
            "kodiaq",
            "octavia",
            "rapid",
            "superb",
            "yeti"
        ]
    }

cars_dict_test = {
        "volkswagen": [
            "arteon",
            "amarok"
        ]
}

if __name__ == "__main__":
    pass