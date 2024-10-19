import math

def get_setlists(page_limit = None):
    
    more_results_available = True
    page = 1


    while more_results_available:

        total_items = 2501
        items_per_page = 20
        number_of_pages = math.ceil(total_items / items_per_page)
        if page % 5 == 0:
            print(f"Page {page} of {number_of_pages} total pages queried.")
        
        # time.sleep(2)

        if page_limit and page >= page_limit:
            more_results_available = False
            print(f"Page {page} of {number_of_pages} total pages queried.")
        
        if page >= number_of_pages:
            more_results_available = False

        page += 1
    # return setlists

get_setlists(12)
print(f"\n{50*'='}\n")
get_setlists()