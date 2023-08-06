from cex.client import *

'''
    CexClient(searchTerm, showLimit)
    Max showLimit = 50
'''

cex = CexClient("cod", 10)
products = cex.priceHigh()
cex.displayResults(products)
