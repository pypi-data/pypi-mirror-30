# Bergholm API Client
Simple Client to fetch products from http://www.bergholm.com/

## Install package
``` pip install bergholm-api-client ```

## Usage
```
from bergholm.api import Client

client = Client(access_token='ABC123')

client.get_caravans()
client.get_caravan('knaus')
client.get_caravan_family('knaus', 'travelino')
client.get_caravan_family_model('knaus', 'travelino', '400-ql')

client.get_motorhomes()
client.get_motorhome('weinsberg')
client.get_motorhome_family('weinsberg', 'carabus')
client.get_motorhome_family_model('weinsberg', 'carabus', '631-me')

```

## Result example:
```json
[{
    u 'image_medium': u 'https://www.bergholm.com/dynamic/brands/knausHV_Mainpic_Wide.jpg',
    u 'slogan': u 'Frihet som ber\xf6r',
    u 'description': u 'I \xf6ver 50 \xe5r har Knaus skapat of\xf6rgl\xf6mliga semester\xf6gonblick, tack vare erfarenhet, hantverkskunnande och gr\xe4nsl\xf6s passion.\xa0Med innovativt nyt\xe4nkande tilltalar Knaus en bred m\xe5lgrupp med det variationsrika programmet.',
    u 'hex': u '0a79c0',
    u 'title': u 'Knaus',
    u 'image_panorama': u 'https://www.bergholm.com/dynamic/brands/panorama/knaushv.jpg',
    u 'type_id': 2,
    u 'image_small': None,
    u 'id': 3,
    u 'rgb': u '10,121,193',
    u 'logo_medium': u 'https://www.bergholm.com/dynamic/logos/knausSmall.png',
    u 'short_description': u 'I \xf6ver 50 \xe5r har Knaus skapat of\xf6rgl\xf6mliga semester\xf6gonblick, tack vare erfarenhet, hantverkskunnande och gr\xe4nsl\xf6s passion.\xa0Med innovativt nyt\xe4nkande tilltalar Knaus en bred m\xe5lgrupp med det variationsrika programmet.',
    u 'logo_big': u 'https://www.bergholm.com/dynamic/logos/knausLarge.png',
    u 'logo_small': None,
    u 'slug': u 'knaus'
}, {
    u 'image_medium': u 'https://www.bergholm.com/dynamic/brands/weinsbergHV_Mainpic_Wide.jpg',
    u 'slogan': u 'Simple | Clever | Smart',
    u 'description': u 'Weinsberg vilar p\xe5 begreppen enkelt, klokt och smart och g\xf6r sk\xe4l f\xf6r detsamma. Med inriktning p\xe5 en yngre m\xe5lgrupp tillverkar man kompletta semestervagnar till mycket attraktiva priser. Enkla men smarta koncept. Weinsbergs modellserier heter CaraOne och CaraTwo och finns i l\xe4ngder fr\xe5n 400 till 750. CaraOne \xe4r robust och smart, med upp till 8 sovplatser finns det gott om utrymme f\xf6r hela familjen. Med CaraOne f\xe5r man helt klart f\xf6r sig att camping \xe4r och ska vara kul! CaraTwo lockar med sin unika kombination av design, moderna l\xf6sningar och ett oslagbart pris. H\xe4r kan du med l\xe4tthet skr\xe4ddarsy ditt eget rullande hotellrum efter smak och behov. CaraTwo, ett personligt anpassat, tekniskt litet underverk.',
    u 'hex': u 'ec7f22',
    u 'title': u 'Weinsberg',
    u 'image_panorama': u 'https://www.bergholm.com/dynamic/brands/panorama/weinsberghv.jpg',
    u 'type_id': 2,
    u 'image_small': None,
    u 'id': 12,
    u 'rgb': u '236,127,34',
    u 'logo_medium': u 'https://www.bergholm.com/dynamic/logos/weinsbergSmall.png',
    u 'short_description': u 'Weinsberg vilar p\xe5 begreppen enkelt, klokt och smart och g\xf6r sk\xe4l f\xf6r detsamma. Med inriktning p\xe5 en yngre m\xe5lgrupp tillverkar man kompletta semestervagnar till mycket attraktiva priser. Enkla men smarta koncept. Weinsbergs modellserier heter CaraOne och CaraTwo och finns i l\xe4ngder fr\xe5n 400 till 750. CaraOne \xe4r robust och smart, och med upp till 8 sovplatser finns det gott om utrymme f\xf6r hela familjen. CaraTwo lockar med sin unika kombination av design och moderna l\xf6sningar till ett oslagbart pris.',
    u 'logo_big': u 'https://www.bergholm.com/dynamic/logos/weinsbergLarge.png',
    u 'logo_small': None,
    u 'slug': u 'weinsberg'
}, {
    u 'image_medium': u 'https://www.bergholm.com/dynamic/brands/tabbertHV_Mainpic_Wide.jpg',
    u 'slogan': u 'Kompromissl\xf6s kvalitet',
    u 'description': u 'Tradition, krav och kvalitet \xe4r av h\xf6gsta prioritet f\xf6r denna tyska husvagnstillverkare. Med mer \xe4n 50 \xe5rs erfarenhet s\xe4tter Tabbert standard bland premiumhusvagnar med absolut h\xf6gsta krav p\xe5 material, form och funktion. Experter arbetar st\xe4ndigt med utvecklingen och kombinerar sofistikerad full\xe4ndning med funktion och design. Tabbert husvagnar \xe4r som sina kunder: distingerade och kr\xe4vande.',
    u 'hex': u '95132b',
    u 'title': u 'Tabbert',
    u 'image_panorama': u 'https://www.bergholm.com/dynamic/brands/panorama/tabberthv.jpg',
    u 'type_id': 2,
    u 'image_small': None,
    u 'id': 6,
    u 'rgb': u '149,19,43',
    u 'logo_medium': u 'https://www.bergholm.com/dynamic/logos/tabbertSmall.png',
    u 'short_description': u 'Tradition, krav och kvalitet \xe4r av h\xf6gsta prioritet f\xf6r denna tyska husvagnstillverkare. Med mer \xe4n 50 \xe5rs erfarenhet s\xe4tter Tabbert standard bland premiumhusvagnar med absolut h\xf6gsta krav p\xe5 material, form och funktion. Tabbert husvagnar \xe4r som sina kunder: distingerade och kr\xe4vande.',
    u 'logo_big': u 'https://www.bergholm.com/dynamic/logos/tabbertLarge.png',
    u 'logo_small': None,
    u 'slug': u 'tabbert'
}, {
    u 'image_medium': u 'https://www.bergholm.com/dynamic/brands/tabHV_Mainpic_Wide.jpg',
    u 'slogan': u 'Attraktiv och okomplicerad',
    u 'description': u 'Denna f\xe4rgstarka husvagnstillverkare har fokuserat p\xe5 mindre husvagnsmodeller med en mycket tydlig gemensam n\xe4mnare - charm. Det h\xe4r \xe4r l\xe4tthanterliga, tuffa, praktiska och mycket v\xe4lbyggda vagnar i uppseendev\xe4ckande former och f\xe4rger, sv\xe5ra att motst\xe5. Den senaste nykomlingen "White" med carbondesign och aluminiumf\xe4lgar har allt man kan beg\xe4ra av en husvagn - men i mindre format. ',
    u 'hex': u '749761',
    u 'title': u 'T@B',
    u 'image_panorama': u 'https://www.bergholm.com/dynamic/brands/panorama/tabhv.jpg',
    u 'type_id': 2,
    u 'image_small': None,
    u 'id': 7,
    u 'rgb': u '116,151,97',
    u 'logo_medium': u 'https://www.bergholm.com/dynamic/logos/tabSmall.png',
    u 'short_description': u 'Denna f\xe4rgstarka husvagnstillverkare har fokuserat p\xe5 mindre husvagnsmodeller med en mycket tydlig gemensam n\xe4mnare - charm. Det h\xe4r \xe4r l\xe4tthanterliga, tuffa, praktiska och mycket v\xe4lbyggda vagnar i uppseendev\xe4ckande former och f\xe4rger, sv\xe5ra att motst\xe5.',
    u 'logo_big': u 'https://www.bergholm.com/dynamic/logos/tabLarge.png',
    u 'logo_small': None,
    u 'slug': u 'tab'
}]
```
