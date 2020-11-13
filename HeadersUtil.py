from random import choice

def get_agents():
    with open('agents', 'r') as fp:
        agents = fp.read().split('\n')
    fp.close()
    return agents

__agents = get_agents()

# proxy and headers
def random_headers():
    return {
        'authority': 'www.trendyol.com',
        'method': 'GET',
        'path': '/kadin+ic-giyim',
        'scheme': 'https',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'max - age = 0',
        'cookie': '__cfduid=db8aa0e05b043ca54db7dc78af3d0dc981597407621; AbTesting=62; _gid=GA1.2.513098808.1597407626; pid=ljZd49AsB3; m=1; sm=1; __cfruid=a7170e55c94c470e5a5864afe6e9dcc6a850eb48-1597407845; COOKIE_TY.IsUserAgentMobileOrTablet=false; SiteHash=x=COOKIE_&pp=ItMm4t5HRy+PG0lVAIiFr6/xslY=&tx=mqeBMUEemR+CB9vIkC5iMa6+zgk=; WebAbTesting=A_33,B_67,C_63,D_23,E_62,F_90,G_90,H_75,I_58,J_43,K_56,L_83,M_19,N_7,O_3,P_51,Q_39,R_35,S_65,T_29,U_16,V_65,W_36,X_12,Y_46,Z_92; NSC_IR-IUUQT-XXX.USFOEZPM.DPN=ffffffff0908147e45525d5f4f58455e445a4a42378b; __RequestVerificationToken=kDOOJFAQQGASIdcDNxdWixiKYg1XhohIhIkKOJTWVNzmxxC_20DNhiFp3jnNF4G4g3vOro3SgUqE1WZaX1Iu8GE7fbTKbur_TJV0FxMJ-NQ1; _gcl_au=1.1.519090647.1597408804; utmSourceGO5d=direct; utmMediumGO5d=not set; utmCampaignGO5d=not set; utmSourceLT30d=direct; utmCampaignLT30d=not set; utmMediumLT30d=not set; utmCampaign30d=not set; utmMedium30d=not set; utmSource30d=direct; utmCampaign30dtemp2=not set; utmSource30dtemp2=direct; utmMedium30dtemp2=not set; _fbp=fb.1.1597408816099.1354449335; COOKIE_TY.Anonym=tx=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1cm46dHJlbmR5b2w6YW5vbmlkIjoiOWQ3ZDIxODUyOThmNDdmZTliYmE1NGQ0NzIzY2I1OGEiLCJhdHdydG1rIjoiODA2NzNkZDAtZDA2YS00OGYyLThlYTctMTBkOTYxNTFkOWE0IiwiaXNzIjoiYXV0aC50cmVuZHlvbC5jb20iLCJhdWQiOiJzYkF5ell0WCtqaGVMNGlmVld5NXR5TU9MUEpXQnJrYSIsImV4cCI6MTc1NTE5MzU3OSwibmJmIjoxNTk3NDA4ODE5fQ.NC6hOBd6SbhJpf9ZfaK6QxQ6FKqsAMBVM5OK7K5MVaw&RefreshToken=027b0c20-756e-4dbe-9215-1c034c569f30; _ym_uid=159740881911796612; _ym_d=1597408819; _ym_isad=2; G_ENABLED_IDPS=google; AbTestingCookies=A_21-B_92-C_55-D_59-E_58-F_50-G_48-H_56-I_13-J_28-K_62-L_14-M_2-N_47-O_94; userid=undefined; sid=BiT2ACgbOn; VisitCount=2; SearchMode=0; trendyolv0=1; _ga_8F2NHTRF7T=GS1.1.1597418562.3.1.1597418959.58; _ga=GA1.2.1056519843.1597407626; _dc_gtm_UA-13174585-1=1; _gat_UA-13174585-1=1',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': choice(__agents)
    }
