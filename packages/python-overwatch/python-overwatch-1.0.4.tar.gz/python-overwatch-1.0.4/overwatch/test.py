# from __init__ import Overwatch

# def main():
#     overwatch = Overwatch(battletag="Okush#11325")

#     print(overwatch(hero="junkrat", filter="hero specific"))
 
#     # print(overwatch(hero="mei", filter="hero specific"))
#     # print(overwatch(hero="dva", filter="combat"))
#     # print(overwatch(hero='doomfist', filter="match awards"))
#     # print(overwatch(hero='roadhog', filter="average"))
#     # print(overwatch(hero='winston', filter="assists"))
#     # print(overwatch(hero='junkrat', filter="hero specific"))
#     # print(overwatch(hero='mccree', filter="hero specific"))
#     # print(overwatch(hero='soldier:76', filter="hero specific"))
from requests_html import HTMLSession

session = HTMLSession()
r = session.get('https://reddit.com')
print(r.html.next())
    


