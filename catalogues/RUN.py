import pip
import subprocess

def import_or_install(package):
    try:
        __import__(package)
    except ImportError:
        pip.main(['install', package])
        
def main():
    package_list = ["scrapy", "img2pdf"]
    for package in package_list:
        import_or_install(package)
    
    print("\n\n\t\t\t----------- GET CATALOGUES -----------")
    print("\n\t*** Using SCRAPY ***")
    print("\n\t1. Get all new catalogues.")
    print("\t2. Get only catalogue or all catalogues from one brand")
    print("\t3. Exit")
    option = input("\n\tEnter: ")
    
    if option == "1":
        subprocess.call(["scrapy", "crawl", "catalogues"])
        print("\n\n\t\t\t***************** FINISH *****************")
    elif option == "2":
        subprocess.call(["scrapy", "crawl", "special-catalogue"])
        print("\n\n\t\t\t***************** FINISH *****************")
    elif option == "3":
        return None
    else:
        print("Wrong number")

    input("Press any keys to Exit")
    
if __name__ == "__main__":
    main()