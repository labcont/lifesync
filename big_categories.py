CATEGORIES_DB = []

def add(words, category):
    for w in words:
        CATEGORIES_DB.append((w, category))


# =========================
# 🍔 ЕДА 
# =========================
add([

# ===== МАГНИТ (ВСЕ ВАРИАЦИИ) =====
"магнит","magnit","mgn","mgnt","magn","magnit mm","magnit express",
"magnitmarket","magnit market","magnitshop","magnit store",
"magnit retail","magnit food","magnit online",
"magnit moskva","magnit spb","magnit ru",
"magnit dostavka","magnit delivery","magnit market ru",

# ===== ПЯТЕРОЧКА =====
"пятерочка","pyaterochka","5ka","5ка","pyater","пятер","fiveka",
"5-ka","five ka","pyaterochka shop","pyaterochka market",
"5ka store","5ka market","pyaterochka express",

# ===== ПЕРЕКРЕСТОК =====
"перекресток","perekrestok","perek","перекр",
"perekrestok market","perekrestok shop","perekrestok express",
"perekrestok retail","crossmarket","cross shop",

# ===== ЛЕНТА =====
"лента","lenta","lent","lnt",
"lenta market","lenta shop","lenta express",
"lenta retail","lenta food","lenta online",

# ===== АШАН =====
"ашан","auchan","auchan ru","ashan","auchan retail",
"auchan market","auchan store","auchan express",
"auchan online","auchan food","auchan shop",

# ===== ОКЕЙ =====
"окей","okey","okej","okey market","okey store",
"okey express","okey retail","okey food",

# ===== ДИКСИ =====
"дикси","dixy","dksi","dixie","dixy market",
"dixy shop","dixy express","dixy retail",

# ===== SPAR =====
"spar","спар","spar market","spar express",
"spar retail","spar food","spar store","spar online",

# ===== METRO =====
"metro","метро","metro cc","metro cash",
"metro market","metro store","metro retail",
"metro food","metro online",

# ===== ВКУСВИЛЛ =====
"вкусвилл","vkusvill","vkus","vv",
"vkusvill market","vkusvill store","vkusvill express",
"vkusvill online","vkusvill food",

# ===== АЗБУКА =====
"азбука вкуса","азбука","abk","av","azbuka vkusa",
"azbuka market","azbuka store","azbuka premium",

# ===== ДОСТАВКИ =====
"самокат","samokat","smkt","samokat food",
"samokat delivery","samokat express",

"яндекс еда","yandex food","yfood","ya food",
"yandex eats","yandex delivery food",

"delivery","delivery club","deliv","dclub",
"delivery service","delivery food",

"яндекс лавка","lavka","yandex lavka",
"lavka food","lavka express",

# ===== ФАСТФУД =====
"kfc","кфс","kfс","kfc food","kfc delivery",

"burger king","бургер кинг","burger","бург",
"burger king food","burger king delivery",

"mcd","mc","mac","мак","макдоналдс",
"mcdonalds","mc donalds","macdonalds",

"вкусно и точка","вкусно","vkusno i tochka",

"subway","сабвей","subway food",
"pizza hut","пицца хат",
"dominos","доминос","dominos pizza",
"dodo pizza","додо","dodo",

# ===== КОФЕ =====
"coffee","кофе","coffee shop","coffee store",
"coffee like","cofix","starbucks","surf coffee",
"coffee house","coffee way","one price coffee",

# ===== МИРОВЫЕ СЕТИ =====
"walmart","walmart store","walmart food",
"costco","costco market",
"aldi","aldi market",
"lidl","lidl food",
"tesco","tesco store",
"carrefour","carrefour market",

"target","target store",
"kroger","kroger market",
"whole foods","whole foods market",
"trader joes","trader joe",

"7eleven","seven eleven","711","7 11",

# ===== ОБЩИЕ =====
"еда","food","foods","продукты","продуктовый",
"кафе","ресторан","столовая","пекарня","еда доставка"

# ===== РОССИЯ (РЕГИОНАЛКИ) =====
"ярче","yarche","yarche market","yarche shop",
"мария ра","maria ra","maria market",
"монетка","monetka","monetka market",
"семишагофф","semishagoff","semi shop",
"бриcтоль","bristol","bristol shop",
"красное и белое","kraskoe beloe","krasnoe beloe","kb shop",
"верный","verny","verny market",
"светофор","svetofor","svetofor shop",
"май","mai market","май магазин",

# ===== ФЕРМЕРСКИЕ =====
"фермер","farmer","farm food","eco food",
"фермерские продукты","eco market","bio food",
"organic food","organic market","bio shop",

# ===== ДОСТАВКИ МИР =====
"uber eats","ubereats","uber food",
"glovo","glovo delivery","glovo food",
"wolt","wolt food","wolt delivery",
"deliveroo","deliveroo food",
"foodpanda","food panda",

# ===== ПИЦЦА =====
"papa johns","papa john","папа джонс",
"little caesars","caesars pizza",
"telepizza","tele pizza",
"pizza express","pizzaexpress",

# ===== БУРГЕРЫ =====
"shake shack","shake shack burger",
"five guys","five guys burger",
"wendys","wendy","wendys burger",

# ===== КОФЕ МИР =====
"tim hortons","tim hortons coffee",
"dunkin","dunkin donuts","dunkin coffee",
"peets coffee","peets","coffee bean",
"blue bottle coffee","blue bottle",

# ===== АЗИЯ =====
"family mart","familymart",
"lawson","lawson store",
"aeon","aeon market",
"lotte mart","lotte",

# ===== ЕВРОПА =====
"rewe","rewe market",
"edka","edka market",
"coop","coop store",
"migros","migros market",

# ===== США СЕТИ =====
"safeway","safeway market",
"publix","publix store",
"heb","heb market",
"meijer","meijer store",
"giant food","giant market",

# ===== ФАСТФУД ДОБИВКА =====
"hardees","hardees burger",
"arbys","arbys food",
"jack in the box","jack box",
"chipotle","chipotle mexican",
"taco bell","taco bell food",

# ===== СУШИ =====
"yakitoriya","якитория",
"tanuki","тануки",
"sushiwok","сушивок",
"sushi master","суши мастер",
"sushi shop","суши шоп",

# ===== ПЕКАРНИ =====
"cinnabon","синнабон",
"paul bakery","paul",
"волконский","volkonsky",
"хлеб насущный","hleb nasushny",

# ===== ОБЩЕЕ =====
"еда онлайн","food online","food shop",
"buy food","order food","еда заказ",
"food delivery service"

# ===== ЕВРОПА =====
"tesco express","tesco extra","tesco metro",
"carrefour express","carrefour city","carrefour hyper",
"lidl plus","lidl store eu","lidl market eu",
"aldi sud","aldi nord","aldi express",
"rewe city","rewe center","rewe to go",
"edka center","edka express","edka store",
"coop prix","coop city","coop supermarket",
"migros city","migros express","migros shop",

# ===== ФРАНЦИЯ / ИТАЛИЯ =====
"auchan drive","auchan city france","auchan direct",
"conad","conad supermercato","conad city",
"esselunga","esselunga market","esselunga store",
"intermarche","intermarche contact","intermarche express",
"leclerc","e leclerc","leclerc drive",

# ===== ИСПАНИЯ =====
"mercadona","mercadona store","mercadona market",
"dias","dia market","super dia",
"eroski","eroski center","eroski city",

# ===== ГЕРМАНИЯ =====
"netto marken discount","netto supermarkt","netto store de",
"penny markt","penny market","penny store",
"tegut","tegut market","tegut store",
"hit supermarkt","hit market","hit store",

# ===== США =====
"wholefoods","wholefoods store","wholefoods shop",
"trader joes market","trader joes store",
"costco wholesale","costco store us",
"sams club","samsclub","sams club store",
"dollar general","dollar general store",
"dollar tree","dollar tree store",

# ===== ФАСТФУД США =====
"in n out","innout","in n out burger",
"whataburger","whataburger food",
"sonic drive in","sonic food","sonic burger",
"white castle","whitecastle","white castle burger",
"culvers","culvers food","culvers burger",

# ===== LATAM =====
"oxxo","oxxo store","oxxo market",
"bodega aurrera","aurrera market","bodega store",
"soriana","soriana market","soriana store",

# ===== АЗИЯ =====
"donki","don quijote","donki store",
"seiyu","seiyu supermarket","seiyu store",
"maxvalu","maxvalu store","maxvalu market",
"ntuc fairprice","fairprice","fairprice store",
"sheng siong","shengsiong","sheng siong market",

# ===== КОРЕЯ =====
"emart","emart store","emart market",
"lotte supermarket","lotte super","lotte store kr",
"homeplus","homeplus market","homeplus store",

# ===== КИТАЙ =====
"hema","hema fresh","hema supermarket",
"alibaba hema","hema store","hema shop",
"jingdong supermarket","jd supermarket china",

# ===== ДОСТАВКИ =====
"getir","getir delivery","getir food",
"gorillas","gorillas delivery","gorillas food",
"flink","flink delivery","flink grocery",
"zapp","zapp delivery","zapp grocery",

# ===== DARK KITCHEN =====
"dark kitchen","ghost kitchen","virtual kitchen",
"kitchen hub","food hub","delivery kitchen",

# ===== БУРГЕРНЫЕ =====
"burger heroes","burgerheroes","bh burger",
"farsh","farsh burger","фарш бургер",
"black star burger","blackstarburger","bs burger",

# ===== ПИЦЦА =====
"pizza 22 cm","pizza22","22cm pizza",
"camorra pizza","camorra","camorra pizza shop",
"brooklyn pizza","brooklyn pizza ru",

# ===== СУШИ =====
"суши весла","sushi vesla","vesla sushi",
"суши бокс","sushi box","sushibox",
"суши тайм","sushi time","sushitime",

# ===== КОФЕ =====
"double b","doubleb coffee","double b cafe",
"skuratov coffee","skuratov","skuratov cafe",
"abc coffee roasters","abc coffee","abc roasters",

# ===== ПЕКАРНИ =====
"bushe","буше","bushe bakery",
"khlebnikoff","хлебников","khleb bakery",
"булочные фокина","fokina bakery","fokina bread",

# ===== АЛКО =====
"wine lab","winelab","wine lab store",
"simplewine","simple wine","simplewine store",
"amwine","am wine","amwine store",

# ===== ОПТ =====
"cash and carry","cash carry","cc market",
"wholesale food","wholesale grocery","bulk food store",

# ===== BIO =====
"bio c bon","biocbon","bio store eu",
"dennree","dennree bio","dennree market",
"alnatura","alnatura market","alnatura store",

# ===== РЫНКИ =====
"рынок","bazaar","food bazaar","fresh bazaar",
"central market","local market","farmers market",

# ===== ОБЩЕЕ =====
"food court","foodcourt","food plaza",
"gastro market","gastrobar","gastro food",
"eatery","eatery place","eatery food"

], "Еда")


# =========================
# 🏠 БЫТ 
# =========================
add([

# ===== OZON =====
"ozon","озон","o3on","oz0n","ozn","ozon ru","ozon shop",

# ===== WILDBERRIES =====
"wildberries","wb","вб","вайлд","wild","wldbrs","wb shop",

# ===== ALIEXPRESS =====
"aliexpress","ali","али","алиэкспресс","aliex","ali exp",

# ===== AMAZON =====
"amazon","амазон","amazon store","amazon shop",

# ===== EBAY =====
"ebay","ебей","ebay store",

# ===== ЯНДЕКС МАРКЕТ =====
"яндекс маркет","yandex market","market","ya market",

# ===== СБЕРМАРКЕТ =====
"сбермаркет","sbermarket","sbm","sber market",

# ===== ТЕХНИКА =====
"dns","днс","dns shop",
"мвидео","mvideo","m vid",
"эльдорадо","eldorado","eld",
"citilink","ситилинк","ctlnk",

# ===== БРЕНДЫ =====
"apple","apple store","эппл",
"samsung","самсунг",
"xiaomi","mi store",

# ===== ДОМ =====
"ikea","икеа","ike",
"leroy merlin","леруа","леруа мерлен",
"obi","оби",
"castorama","касторама",
"hoff","хофф",

# ===== ОДЕЖДА =====
"zara","hm","h&m","bershka","pullbear","reserved",
"uniqlo","asos","lamoda","shein","zalando",

# ===== СПОРТ =====
"nike","adidas","reebok","puma","sportmaster",

# ===== ЛЮКС =====
"gucci","prada","louis vuitton","lv","balenciaga",

# ===== ОБЩЕЕ =====
"shop","shopping","store","заказ","товары"

# ===== МАРКЕТПЛЕЙСЫ МИР =====
"rakuten","rakuten shop","rakuten market",
"flipkart","flipkart store","flipkart online",
"shopify","shopify store","shopify shop",
"etsy","etsy shop","etsy store",
"allegro","allegro market","allegro store",
"cdiscount","cdiscount store","cdiscount market",
"bol.com","bol store","bol market",

# ===== ЕВРОПА ONLINE =====
"zalando lounge","zalando store eu",
"otto","otto shop","otto market",
"about you","aboutyou","aboutyou shop",
"asos marketplace","asos shop",
"notino","notino store","notino market",

# ===== ЭЛЕКТРОНИКА МИР =====
"best buy","bestbuy","best buy store",
"newegg","newegg store","newegg market",
"micro center","microcenter","micro center store",
"bh photo","b&h","bhphotovideo",
"adorama","adorama store","adorama shop",

# ===== КИТАЙ / АЗИЯ =====
"taobao","taobao market","taobao shop",
"tmall","tmall store","tmall market",
"jd","jd store","jd market",
"pinduoduo","pdd","pinduoduo shop",
"shopee","shopee store","shopee market",
"lazada","lazada store","lazada market",

# ===== РОССИЯ ONLINE =====
"beru","беру","beru market",
"goods ru","goodsru","goods market",
"utkonos","утконос","utkonos online",
"holodilnik ru","holodilnik","holodilnik store",
"technopark","технопарк","technopark store",

# ===== ТЕХНИКА (БРЕНДЫ) =====
"sony store","sony shop","sony online",
"lg store","lg shop","lg electronics store",
"bosch store","bosch shop","bosch online",
"philips store","philips shop",
"lenovo store","lenovo shop","lenovo online",
"dell store","dell shop","dell online",
"hp store","hp shop","hp online",

# ===== APPLE / SAMSUNG ДОБИВКА =====
"apple com","apple online store","apple retail",
"samsung store online","samsung shop ru",
"samsung electronics store",

# ===== МЕБЕЛЬ =====
"jysk","jysk store","jysk market",
"home24","home24 shop","home24 market",
"wayfair","wayfair store","wayfair online",
"westwing","westwing store","westwing shop",
"maisons du monde","maisonsdumonde",

# ===== ДОМ / DIY =====
"screwfix","screwfix store","screwfix shop",
"toolstation","toolstation store",
"bauhaus","bauhaus store","bauhaus market",
"hornbach","hornbach store","hornbach market",

# ===== ОДЕЖДА МИР =====
"primark","primark store","primark shop",
"gap","gap store","gap shop",
"old navy","oldnavy","old navy store",
"forever 21","forever21","forever 21 shop",
"massimo dutti","massimo store",

# ===== ОБУВЬ =====
"foot locker","footlocker","foot locker store",
"deichmann","deichmann store","deichmann shop",
"ecco","ecco shoes","ecco store",
"clarks","clarks shoes","clarks store",

# ===== СПОРТ =====
"decathlon","decathlon store","decathlon shop",
"sportmaster","спортмастер","sportmaster store",
"intersport","intersport store","intersport shop",

# ===== КОСМЕТИКА =====
"sephora","sephora store","sephora shop",
"ulta","ulta beauty","ulta store",
"letual","летуаль","letual store",
"rive gauche","рив гош","rivegauche",

# ===== АПТЕКИ =====
"аптека","apteka","pharmacy store",
"eapteka","еаптека","eapteka online",
"36 6","36и6","36.6 pharmacy",
"rigla","ригла","rigla pharmacy",

# ===== АВТО ТОВАРЫ =====
"exist","exist ru","exist auto",
"emex","emex ru","emex auto",
"autodoc","autodoc ru","autodoc store",
"autoru store","auto parts shop",

# ===== ДЕТСКИЕ =====
"detsky mir","детский мир","detsky mir store",
"toys r us","toysrus","toys r us store",
"mothercare","mothercare store",

# ===== КНИГИ =====
"labirint","лабиринт","labirint store",
"ozon books","book store online",
"chitai gorod","читай город","chitai store",

# ===== ЮВЕЛИРКА =====
"pandora","pandora store","pandora shop",
"sokolov","соколов","sokolov store",
"sunlight","санлайт","sunlight store",

# ===== ЛЮКС =====
"armani","armani store","armani shop",
"versace","versace store",
"dior","dior store","dior shop",
"chanel","chanel store",

# ===== МУСОР / ОШИБКИ =====
"oz0nru","ozonru","ozonn","ozon shop ru",
"wildberies","wildberriesru","wb shop ru",
"aliexpres","aliexpressru","ali shop ru",

# ===== GENERIC =====
"online shop","internet store","web store",
"ecommerce","e commerce","online purchase",
"buy online","shopping online","store online"

# ===== DNS ДОБИВКА =====
"dns retail","dns market","dns online","dns ru","dns shop ru",
"dns electronics","dns store ru","dns technic",

# ===== М.ВИДЕО ДОБИВКА =====
"mvideo store","mvideo retail","mvideo online","mvideo ru",
"mvideo shop ru","mvideo electronics","mvideo market",

# ===== ЭЛЬДОРАДО ДОБИВКА =====
"eldorado store","eldorado retail","eldorado online",
"eldorado ru","eldorado shop ru","eldorado electronics",

# ===== СИТИЛИНК ДОБИВКА =====
"citilink store","citilink online","citilink retail",
"citilink ru","citilink shop ru","citilink electronics",

# ===== ОНЛАЙН ТЕХНИКА РФ =====
"pleer ru","pleer","pleer store","pleer shop",
"oldi","oldi store","oldi market",
"regard","regard store","regard market",
"xcom","x com","xcom shop","xcom store",

# ===== МЕБЕЛЬ РФ =====
"hoff market","hoff store","hoff online",
"shatura","shatura mebel","shatura store",
"ангстрем","angstrem","angstrem mebel",
"много мебели","mnogo mebeli","mnogo mebeli store",
"divan ru","divanru","divan store",
"askona","askona store","askona shop",

# ===== DIY РФ =====
"petrovich","петрович","petrovich store",
"220 volt","220volt","220 volt store",
"vseinstrumenty","все инструменты","vseinstrumenty ru",
"instrument ru","instrument shop",
"maxidom","максидом","maxidom store",

# ===== ОДЕЖДА РФ =====
"gloria jeans","gloriajeans","gloria store",
"befree","befree store","befree shop",
"ostin","ostin store","ostin shop",
"sela","sela store","sela shop",
"love republic","loverepublic","love republic store",
"zarina","zarina store","zarina shop",

# ===== МАРКЕТПЛЕЙСЫ РФ ДОБИВКА =====
"kazanexpress","kazan express","kazanexpress store",
"wildberries ru","wb ru","wb online",
"ozon express","ozon fresh","ozon delivery",
"megamarket ru","sber mega market",

# ===== ПРОДУКТОВЫЕ ONLINE =====
"утконос онлайн","utkonos delivery","utkonos shop",
"самокат маркет","samokat shop ru",
"яндекс лавка магазин","lavka shop ru",

# ===== КОСМЕТИКА РФ =====
"gold apple","goldapple","gold apple store",
"podruzhka","подружка","podruzhka store",
"ile de beaute","иль де ботэ","iledebeaute",

# ===== АПТЕКИ ДОБИВКА =====
"аптека ру","apteka ru","apteka online",
"zdravcity","здравсити","zdravcity store",
"asna","асна","asna pharmacy",

# ===== ДЕТСКИЕ РФ =====
"korablik","кораблик","korablik store",
"dochki synochki","дочки сыночки","dochki synochki store",

# ===== КНИГИ РФ =====
"bookvoed","буквоед","bookvoed store",
"respublica","республика","respublica store",

# ===== ЮВЕЛИРКА РФ =====
"585 gold","585","585 gold store",
"adamas","adamas store","adamas shop",
"zoloto 585","золото 585",

# ===== АВТО РФ =====
"exist ru shop","emex shop ru","autodoc shop ru",
"autoall","autoall store","autoall shop",
"колеса даром","kolesa darom","kolesa darom shop",

# ===== ЭЛЕКТРОНИКА МАЛЫЕ =====
"onlinetrade","onlinetrade ru","onlinetrade store",
"just ru","just store","just market",
"nix","nix ru","nix store",

# ===== ХОЗТОВАРЫ =====
"fix price shop","fixprice store ru",
"galamart","галамарт","galamart store",
"hozmir","хозмир","hozmir store",

# ===== ОШИБКИ / ИСКАЖЕНИЯ =====
"dnsru","dnsshop","mvideo ruu","eldoradoru",
"citilinkru","ozonruu","wbshop","wildbrries",

# ===== GENERIC РФ =====
"интернет магазин","онлайн магазин","магазин онлайн",
"купить онлайн","заказ онлайн","товары онлайн",
"покупка онлайн","интернет покупка"

# ===== ЭЛЕКТРОНИКА РФ (НОВЫЕ) =====
"citilink mini","citilink pro","citilink express",
"dns discount","dns market ru","dns hyper",
"mvideo discount","mvideo sale","mvideo pro",
"eldorado sale","eldorado discount","eldorado pro",

# ===== РИТЕЙЛ ТЕХНИКИ =====
"electronika ru","electronika shop","electronika market",
"tehnopoint","технопоинт","tehnopoint store",
"tehnosila","техносила","tehnosila store",
"pozitronika","позитроника","pozitronika shop",

# ===== ОНЛАЙН РИТЕЙЛ РФ =====
"goodsmarket","goods online ru","goods shop ru",
"ru market","ru store","russian store",
"market ru shop","online store ru",

# ===== ЛОКАЛЬНЫЕ МАРКЕТЫ =====
"gorod market","город маркет","город магазин",
"city market ru","city shop ru",
"region market","регион маркет","регион магазин",

# ===== СТРОЙКА РФ ДОБИВКА =====
"stroymarket","строймаркет","stroymarket shop",
"stroyland","стройландия","stroyland shop",
"stroy depot","строй депо","stroy depot shop",
"megastroy","мегастрой","megastroy store",

# ===== МЕБЕЛЬ РФ ДОБИВКА =====
"mebelvia","мебельвиа","mebelvia shop",
"mebelion","мебелион","mebelion store",
"bestmebel","best mebel","bestmebel shop",
"mebel market ru","мебель маркет",
"divany tut","диваны тут","divany tut shop",

# ===== DIY / РЕМОНТ =====
"remont market","ремонт маркет","remont shop",
"master tools","мастер тулс","mastertools shop",
"stroi baza","строй база","stroibaza shop",
"instrumenty ru","инструменты ру",

# ===== ОДЕЖДА РФ ДОБИВКА =====
"modis","modis store","modis shop",
"incity","incity store","incity shop",
"kari","kari store","kari shop",
"kari kids","kari kids store",
"oodji","oodji store","oodji shop",

# ===== ОБУВЬ РФ =====
"ralf ringer","ralf ringer store","ralf shop",
"respect shoes","respect store",
"chester shoes","chester store",
"tamaris ru","tamaris store",

# ===== МАРКЕТЫ ОДЕЖДЫ =====
"fashion store ru","fashion market ru",
"clothes shop ru","одежда магазин",
"moda market","мода маркет","moda shop",

# ===== ДЕТСКИЕ РФ ДОБИВКА =====
"akusherstvo","akusherstvo ru","akusherstvo store",
"detmir online","detmir shop ru",
"kids store ru","детский магазин",

# ===== КАНЦЕЛЯРКА =====
"komus","комус","komus store",
"office market","office shop ru",
"kanzler","канцлер магазин",
"kanc market","канцтовары магазин",

# ===== ХОЗТОВАРЫ РФ =====
"hozmarket","хозмаркет","hozmarket store",
"domovoy","домовой","domovoy store",
"dommarket","доммаркет","dommarket shop",

# ===== КОСМЕТИКА РФ ДОБИВКА =====
"rive gauche ru","rivegauche store ru",
"letual online","letual shop ru",
"beauty market ru","beauty shop ru",

# ===== АПТЕКИ РФ ЕЩЕ =====
"pharm market","pharmacy ru","pharmacy shop ru",
"apteka shop","аптека магазин",

# ===== АВТО ДОБИВКА =====
"autopiter","автопитер","autopiter store",
"exist shop ru","emex online ru",
"auto market ru","авто магазин",

# ===== КНИГИ ДОБИВКА =====
"book market ru","bookshop ru","книжный магазин",
"читатель","chitatel store",

# ===== ЮВЕЛИРКА ДОБИВКА =====
"zoloto market","золото магазин",
"gold store ru","ювелир магазин",

# ===== СПОРТ РФ ДОБИВКА =====
"sportmarket","спортмаркет","sportmarket store",
"sport shop ru","спорт магазин",

# ===== ГИПЕРМАРКЕТЫ =====
"mega store ru","mega market ru",
"hypermarket ru","гипермаркет",
"supermarket ru","супермаркет магазин",

# ===== УНИВЕРСАЛЬНЫЕ =====
"shop ru","store ru","market ru",
"ru online shop","ru ecommerce",
"russia shop","russia market",

# ===== ОШИБКИ / ИСКАЖЕНИЯ РФ =====
"ozonn","ozonr","wbrr","wildb",
"citilnk","eldorad","mvidio",
"dnss","dnsr","technoprk",

# ===== GENERIC ЖЕСТЬ =====
"покупка товар","заказ товар","купить товар",
"интернет заказ","онлайн покупка",
"магазин рф","покупка рф","заказ рф"

], "Быт")


# =========================
# 🚗 ТРАНСПОРТ (ЖЕСТКО 1000+)
# =========================
add([

# ===== ТАКСИ РФ =====
"yandex go","yandexgo","яндекс го","яндекс такси","yandex taxi","yandex.taxi",
"uber","uber trip","uber ride","uber bv",
"bolt","bolt taxi","bolt ride",
"citymobil","ситимобил","city mobil","citymobil ride",
"gett","gett taxi","gett ride",
"maxim","такси максим","taxi maxim","maxim ride",

# ===== КАРШЕРИНГ РФ =====
"delimobil","делимобиль","delimobil ride","delimobil car",
"belkacar","belka car","belka","belkacar ride",
"youdrive","you drive","youdrive car",
"rentmee","rent me","rentmee car",
"anytime","anytime car","anytime carsharing",

# ===== ОБЩИЙ ТРАНСПОРТ =====
"метро","metro transport","mosmetro","mos metro",
"автобус","bus","bus ticket","bus transport",
"трамвай","tram","tramway",
"троллейбус","trolleybus",

# ===== РЖД / ПОЕЗДА =====
"ржд","rzd","rzd ticket","rzd ru","rzd bonus",
"ржд билеты","rzd train","train ticket","railway ticket",
"ту ту","tutu","tutu ru","tutu travel",

# ===== АВИА =====
"aeroflot","аэрофлот","aeroflot ticket",
"s7","s7 airlines","s7 ticket",
"pobeda","победа","pobeda airlines",
"utair","utair ticket",
"ural airlines","уральские авиалинии",

# ===== АВИА АГРЕГАТОРЫ =====
"aviasales","aviasales ru","aviasales ticket",
"skyscanner","skyscanner ticket",
"kupibilet","купи билет","kupibilet ru",
"one two trip","onetwotrip","onetwo trip",

# ===== ТОПЛИВО / АЗС РФ =====
"лукойл","lukoil","lukoil azs","lukoil fuel",
"газпром","gazprom","gazpromneft","gazprom fuel",
"роснефть","rosneft","rosneft azs",
"татнефть","tatneft","tatneft fuel",
"нефтьмагистраль","neftmagistral","nm fuel",
"bp","bp fuel","bp station",
"shell","shell fuel","shell station",

# ===== ПАРКОВКИ =====
"parking","парковка","паркинг","parking ru",
"mos parking","мос парковка","mosparking",
"parking app","city parking",

# ===== САМОКАТЫ / BIKE =====
"whoosh","whoosh ride","whoosh scooter",
"urent","urent bike","urent scooter",
"lite","lite scooter","lite ride",
"yandex scooter","яндекс самокат",

# ===== ЛОГИСТИКА / ДОСТАВКА =====
"cdek","сдэк","cdek delivery","cdek express",
"boxberry","боксберри","boxberry delivery",
"dpd","dpd delivery","dpd ru",
"pony express","ponyexpress","pony delivery",
"dhl","dhl express","dhl delivery",
"fedex","fedex delivery",
"ups","ups delivery",

# ===== КУРЬЕРКИ =====
"доставка","delivery transport","courier",
"courier service","express delivery",
"грузоперевозки","cargo transport","logistics",

# ===== АВТО СЕРВИСЫ =====
"автосервис","car service","auto service",
"шиномонтаж","tire service","tire change",
"мойка","car wash","автомойка",

# ===== ЗАПРАВКИ / ЗАРЯДКИ =====
"charge","charging","ev charging",
"electric charge","tesla supercharger",
"зарядка авто","электрозаправка",

# ===== ПЛАТНЫЕ ДОРОГИ =====
"toll road","платная дорога","road toll",
"автодор","avtodor","avtodor pay",

# ===== КАРТЫ / НАВИГАЦИЯ =====
"yandex maps","яндекс карты","maps navigation",
"google maps","gmaps","navigation app",

# ===== АРЕНДА АВТО =====
"rent car","car rent","car rental",
"rentalcars","rental car service",
"hertz","hertz rent","avis","avis rent",
"europcar","europcar rent",

# ===== ОШИБКИ / СМЕЩЕНИЯ =====
"yanedx go","yadnex taxi","uberr","uberride",
"boltt","delimobill","belkacarr",
"lukoill","gazpromm","rosnefft",
"cdekk","boxbery","dpdd",

# ===== GENERIC =====
"taxi ride","trip","поездка","transport",
"транспорт","дорога","проезд",
"ticket","билет","travel transport"

# ===== РЕГИОНАЛЬНЫЕ ТАКСИ РФ =====
"такси везет","taxi vezet","vezet ride",
"лидер такси","taxi lider","lider ride",
"поехали такси","poehali taxi","poehali ride",
"сатурн такси","saturn taxi","saturn ride",
"таксовичкоф","taxovichkof","taxovichkof ride",
"евротакси","eurotaxi","euro taxi ride",

# ===== МЕЖДУГОРОДНИЕ ПЕРЕВОЗКИ =====
"blablacar","блаблакар","bla bla car","blabla ride",
"busfor","busfor ticket","busfor ru",
"ecolines","ecolines bus","ecolines ticket",
"flixbus","flix bus","flixbus ticket",

# ===== РЖД ДОБИВКА =====
"rzd online","rzd pass","rzd pay","rzd travel",
"rail ticket","train russia","railway rzd",
"express train","скоростной поезд","ласточка","sapsan","сапсан",

# ===== АЭРОПОРТЫ =====
"sheremetyevo","шереметьево","svo airport",
"domodedovo","домодедово","dme airport",
"vnukovo","внуково","vko airport",
"pulkovo","пулково","led airport",
"airport service","airport transfer",

# ===== ТАКСИ АЭРОПОРТ =====
"airport taxi","transfer airport","airport ride",
"такси аэропорт","трансфер аэропорт",

# ===== ПАРКИНГ ДОБИВКА =====
"parking moscow","parking spb","city parking ru",
"underground parking","paid parking","street parking",
"парковка центр","парковка тц",

# ===== АВТО ДОРОГИ =====
"road pay","highway toll","expressway",
"м11","м4 дон","м12 трасса",
"toll moscow","road payment ru",

# ===== ЭЛЕКТРО ТРАНСПОРТ =====
"electro scooter","e scooter","escooter",
"bike sharing","велопрокат","bike rent",
"велобайк","velobike","velobike ru",

# ===== ЛОГИСТИКА РФ ДОБИВКА =====
"пэк","pek","pek delivery","pek cargo",
"деловые линии","dellin","dellin ru","dellin delivery",
"желдорэкспедиция","jeldor","rail cargo",
"байкал сервис","baikalsr","baikalsr delivery",
"kit transport","тк кит","kit cargo",

# ===== АВТОПАРКИ =====
"fleet","car fleet","auto fleet",
"таксопарк","taxi park","taxi fleet",

# ===== ШТРАФЫ / ГИБДД =====
"штраф гибдд","gibdd fine","traffic fine",
"pay fine","штраф оплата","fine payment",
"госуслуги штраф","gosuslugi fine",

# ===== СТРАХОВКА АВТО =====
"осаго","osago","osago payment",
"каско","kasko","car insurance",
"insurance auto","auto insure",

# ===== МОЙКИ / СЕРВИСЫ =====
"detailing","car detailing","auto detailing",
"мойка самообслуживания","self car wash",
"авто детейлинг","detail center",

# ===== ЗАПЧАСТИ / СЕРВИС =====
"autoparts","auto parts","car parts",
"запчасти авто","parts store auto",
"service auto","repair auto",

# ===== ПЛАТЕЖИ ЗА ПРОЕЗД =====
"troika","тройка карта","troika card",
"podorozhnik","подорожник карта",
"transport card","travel card",
"metro card","bus card",

# ===== НАВИГАЦИЯ ДОБИВКА =====
"navitel","навител","navitel navigation",
"2gis","2гис","2gis maps",
"maps me","mapsme","offline maps",

# ===== ГРУЗОПЕРЕВОЗКИ =====
"груз такси","cargo taxi","truck delivery",
"грузовичкоф","gruzovichkof","truck service",
"перевозка грузов","cargo move",

# ===== ОШИБКИ / КРИВЫЕ =====
"taxii","taksi","taksii","uberru",
"yandextaxi","yandexgooo","delimobilll",
"cdekkk","dellinn","pekruu",

# ===== GENERIC =====
"ride payment","trip payment","transport payment",
"travel payment","ticket payment",
"поездка оплата","оплата транспорт"

], "Транспорт")


# =========================
# 🎮 РАЗВЛЕЧЕНИЯ (500+)
# =========================
add([

# ===== СТРИМИНГ ВИДЕО =====
"netflix","netflix com","netflix subscription",
"ivi","ivi ru","ivi online",
"okko","okko tv","okko online",
"kinopoisk","кинопоиск","kinopoisk hd",
"wink","wink tv","wink online",
"more tv","more.tv","more tv online",
"start","start ru","start online",
"premier","premier one","premier online",

# ===== ВИДЕО ПЛАТФОРМЫ =====
"youtube","youtube premium","youtube music",
"rutube","рутуб","rutube video",
"vk video","вк видео","vkvideo",
"dailymotion","vimeo","twitch","twitch tv",

# ===== МУЗЫКА =====
"spotify","spotify premium",
"yandex music","яндекс музыка","ymusic",
"vk music","boom","boom music",
"apple music","itunes","itunes store",
"youtube music app",
"deezer","soundcloud",

# ===== ИГРЫ ПЛАТФОРМЫ =====
"steam","steam store","steam games",
"epic games","epic store","epicgames",
"origin","ea app","ea games",
"battle net","battlenet","blizzard",
"uplay","ubisoft connect",
"gog","gog com","gog games",

# ===== КОНСОЛИ =====
"playstation","ps store","psn","ps plus",
"xbox","xbox live","xbox game pass",
"nintendo","nintendo eshop","switch store",

# ===== МОБИЛЬНЫЕ ИГРЫ =====
"app store game","google play game",
"donate game","game purchase",
"in app purchase","игра донат",

# ===== КИНО / ТЕАТР =====
"кино","cinema","movie","film",
"кинотеатр","cinema ticket","movie ticket",
"театр","theatre","theater ticket",
"концерт","concert","concert ticket",
"шоу","show ticket","live show",

# ===== БИЛЕТЫ =====
"kassir","кассир","kassir ru",
"parter","parter ru","ticketland",
"ticketland ru","concert ru",
"tickets ru","event ticket",

# ===== НОЧНАЯ ЖИЗНЬ =====
"клуб","night club","nightclub",
"бар","bar","pub",
"караоке","karaoke","karaoke bar",
"вечеринка","party","afterparty",
"lounge","lounge bar","hookah lounge",

# ===== КАЛЬЯНЫ / АЛКО =====
"hookah","кальян","hookah bar",
"алкоголь","alcohol","drink",
"пиво","beer","craft beer",
"вино","wine","wine bar",
"водка","vodka","whiskey","rum","tequila",

# ===== СТАВКИ / АЗАРТ =====
"ставки","bet","betting",
"fonbet","фонбет",
"winline","винлайн",
"liga stavok","лига ставок",
"parimatch","париматч",
"1xbet","1xstavka",
"букмекер","bookmaker",
"casino","казино","online casino",
"slot","slots","slot machine",

# ===== КИБЕРСПОРТ =====
"esports","киберспорт","cybersport",
"dota","csgo","counter strike",
"valorant","league of legends",
"tournament","gaming tournament",

# ===== VR / АРКАДЫ =====
"vr club","vr game","virtual reality",
"игровой клуб","game club",
"arcade","arcade games","игровые автоматы",

# ===== ТВ / ПОДПИСКИ =====
"tv subscription","подписка тв",
"online tv","internet tv",
"smart tv apps","tv app",

# ===== СТРИМЫ / ДОНАТЫ =====
"donate","донат","donation stream",
"stream support","поддержка стримера",
"twitch donate","youtube donate",

# ===== ЗНАКОМСТВА =====
"tinder","тиндер","dating app",
"badoo","badoo app",
"mamba","мамба",
"dating","online dating",

# ===== ОБЩЕЕ =====
"развлечения","entertainment",
"досуг","leisure",
"fun","activity","event",
"афиша","events","куда сходить",

# ===== ОШИБКИ / ИСКАЖЕНИЯ =====
"netfliix","spotfy","youtubee",
"steeam","epicgmes","playstaton",
"xboxx","nintendoo",
"кинопоискк","ивии","оккоо",

# ===== GENERIC =====
"watch movie","watch online",
"listen music","music subscription",
"play game","buy game",
"night life","go club",
"buy ticket","order ticket",
"event booking","entertainment app"

# ===== РАЗВЛЕЧЕНИЯ РФ ДОБИВКА =====
"vk play","vkplay","vk play games",
"mygames","my games","mygames store",
"mail ru games","mailru games",

# ===== РУССКИЕ СТРИМИНГИ =====
"ntv plus","нтв плюс","ntvplus",
"tricolor tv","триколор","tricolor online",
"smotreshka","смотрешка","smotreshka tv",
"peers tv","peerstv","peers tv app",

# ===== КИНОСЕТИ РФ =====
"каро","karo cinema","karo film",
"синема парк","cinema park","cinemapark",
"формула кино","formula kino","formula cinema",
"люксор","luxor cinema","luxor",
"пять звезд кино","5 stars cinema",

# ===== ТЕАТРЫ / КОНЦЕРТЫ РФ =====
"bolshoi theatre","большой театр",
"mariinsky","мариинский театр",
"lenkom","ленком",
"театр сатиры","satire theatre",
"театр наций","theatre of nations",

# ===== БИЛЕТЫ РФ ДОБИВКА =====
"yandex afisha","яндекс афиша","afisha ru",
"afisha","afisha events","afisha tickets",
"concert moscow","concert spb",

# ===== КВЕСТЫ / АКТИВНОСТИ =====
"quest room","квест","quest game",
"escape room","escape quest",
"laser tag","лазертаг","lasertag",
"paintball","пейнтбол",
"bowling","боулинг","bowling club",
"billiard","бильярд","billiards club",

# ===== ПАРКИ / АТТРАКЦИОНЫ =====
"attraction park","amusement park",
"парк развлечений","аттракционы",
"roller coaster","theme park",
"zoo","зоопарк","aquapark","аквапарк",
"океанариум","oceanarium",

# ===== СТЕНДАП / ШОУ =====
"standup","stand up","стендап",
"comedy club","камеди клаб",
"improv show","импровизация",
"юмор шоу","humor show",

# ===== ФЕСТИВАЛИ =====
"festival","фестиваль","music festival",
"open air","openair","open air event",
"concert festival","summer fest",

# ===== ХОББИ / ТВОРЧЕСТВО =====
"мастер класс","master class",
"art studio","арт студия",
"drawing class","рисование",
"dance class","танцы",
"music school","музыкальная школа",

# ===== СПОРТ РАЗВЛЕКАТЕЛЬНЫЙ =====
"fitness club","фитнес клуб",
"gym","тренажерный зал",
"yoga","йога студия",
"pilates","пилатес",
"crossfit","кроссфит",

# ===== СТРИМЕРЫ / ДОНАТЫ ДОБИВКА =====
"donate alert","donationalerts",
"boosty","boosty to",
"patreon","patreon support",

# ===== АНИМЕ / КОМИКСЫ =====
"anime","аниме","anime online",
"manga","манга","manga reader",
"comic","comics","comic store",
"webtoon","webtoon app",

# ===== ПОРНО / 18+ =====
"porn","porno","xxx",
"adult video","adult content",
"18 plus","18+","sex video",

# ===== VR ДОБИВКА =====
"vr arena","vr park","vr entertainment",
"virtual games","vr zone",

# ===== АНТИКИНО / АРТ =====
"art house","arthouse cinema",
"indie film","independent cinema",
"film festival","cinema festival",

# ===== ИГРЫ ДОБИВКА =====
"game center","gaming hub",
"pc club","пк клуб","computer club",
"lan party","lan gaming",

# ===== НАСТОЛКИ =====
"board games","настольные игры",
"boardgame club","table games",
"dnd","dungeons and dragons",

# ===== КВИЗЫ =====
"quiz","квиз","quiz game",
"pub quiz","bar quiz",

# ===== КАЛЬЯН ДОБИВКА =====
"shisha","shisha lounge",
"hookah place","hookah club",

# ===== ОШИБКИ ДОБИВКА =====
"spootify","youtub","netflox",
"kinoposk","okkoo","ivii ruu",
"steem","epicc","playstatn",

# ===== GENERIC ЕЩЕ =====
"have fun","spend time",
"evening plans","weekend plans",
"куда пойти","чем заняться",
"досуг вечер","развлечься"

# ===== НОВЫЕ СТРИМИНГИ / ПЛАТФОРМЫ =====
"paramount plus","paramount+","paramount streaming",
"disney plus","disney+","disney streaming",
"hbo max","max streaming","hbo subscription",
"peacock tv","peacock streaming",
"crunchyroll","crunchyroll anime",
"funimation","funimation anime",

# ===== РУССКИЕ ВИДЕО / КОНТЕНТ =====
"сериал","сериалы","смотреть сериал",
"фильм онлайн","смотреть фильм",
"видео сервис","видеосервис",
"онлайн кино","онлайн фильмы",

# ===== МУЗЫКА ДОБИВКА (РУ) =====
"музыка","слушать музыку",
"музыкальный сервис","муз сервис",
"плейлист","playlist",
"трек","music track",
"альбом","music album",

# ===== ИГРЫ (РУ) =====
"игры","играть","купить игру",
"игровой магазин","game shop",
"донат в игре","донатить",
"игровая валюта","game currency",

# ===== КИБЕРСПОРТ ДОБИВКА =====
"турнир","турнир по играм",
"кибер турнир","esport match",
"игровое соревнование",

# ===== КИНО / ТЕАТР (РУ ДОБИВКА) =====
"билет в кино","билет кино",
"поход в кино","сходить в кино",
"билет в театр","театр билет",
"спектакль","театральный спектакль",

# ===== КОНЦЕРТЫ / ШОУ =====
"живой концерт","концерт билет",
"музыкальное шоу","шоу программа",
"выступление","live performance",

# ===== БИЛЕТЫ (РУ ДОБИВКА) =====
"купить билет","заказ билета",
"билет онлайн","электронный билет",
"афиша событий","расписание мероприятий",

# ===== НОЧНАЯ ЖИЗНЬ (РУ ДОБИВКА) =====
"ночная жизнь","ночной клуб",
"сходить в бар","бар вечером",
"выпить","пойти в клуб",

# ===== АЛКО РАСШИРЕНИЕ =====
"коктейль","cocktail","bar drinks",
"алко","алко бар","drinks bar",

# ===== КАЛЬЯН ДОБИВКА RU =====
"кальянная","hookah place ru",
"покурить кальян","кальян бар",

# ===== ЗНАКОМСТВА ДОБИВКА =====
"знакомства","сайт знакомств",
"найти девушку","найти парня",
"dating service","match app",

# ===== АКТИВНЫЕ РАЗВЛЕЧЕНИЯ =====
"каток","ice skating",
"скейт парк","skate park",
"картинг","karting",
"батут","trampoline park",
"скалодром","climbing gym",

# ===== ПАРКИ / ПРОГУЛКИ =====
"прогулка","гулять","парк",
"городской парк","зона отдыха",

# ===== ДЕТСКИЕ РАЗВЛЕЧЕНИЯ =====
"детский центр","детская комната",
"развлечения для детей",
"kids entertainment","kids play zone",

# ===== ХОББИ ДОБИВКА =====
"хобби","занятие","увлечение",
"handmade","ручная работа",
"лепка","craft hobby",

# ===== ТВ ДОБИВКА =====
"телевидение","тв онлайн",
"смотреть тв","тв каналы",
"телеканал","tv channel",

# ===== СТРИМЫ ДОБИВКА RU =====
"стрим","стример","смотреть стрим",
"поддержка стрима","донат стримеру",

# ===== АНИМЕ ДОБИВКА RU =====
"аниме сериал","смотреть аниме",
"манга онлайн","читать мангу",

# ===== КОМИКСЫ RU =====
"комиксы","читать комиксы",
"магазин комиксов",

# ===== НАСТОЛКИ RU =====
"настолки","играть в настолки",
"клуб настольных игр",

# ===== КВИЗЫ RU =====
"квиз вечер","игра квиз",
"интеллектуальная игра",

# ===== ФЕСТИВАЛИ RU =====
"музыкальный фестиваль",
"летний фестиваль",
"городской фестиваль",

# ===== GENERIC РУССКИЙ БУСТ =====
"отдых","отдыхать","развлечься",
"провести время","куда сходить вечером",
"вечерний отдых","досуг выходные",
"заняться чем то","как развлечься",

# ===== ЕЩЕ ОШИБКИ =====
"netfliks","spotifi","youtubee ru",
"kinopoiskk ru","okko tvv",
"twich","twich tv",
"spoti fy","you tube"

# ===== RU ДОНАТ СЕРВИСЫ =====
"донатов нет","донатовнет","donatov net","donatov.net",
"донат","донаты","донат сервис",
"донат сайт","донат оплата",
"донат в игру","донат игра",

"funpay","fun pay","funpay ru","funpay.com",
"funnpay","funpey",

"ggsel","gg sel","ggsel net","ggsel.net",
"g g sel",

"plati ru","plati.ru","plati market",
"oplata info","oplata.info",

"donationalerts","donation alerts","донейшн алертс",
"donatepay","donate pay","донейт пей",

"boosty","boosty to","бусти","boosty.to",
"patreon","patreon com","патреон",

# ===== ИГРОВЫЕ ВАЛЮТЫ =====
"пополнение игры","пополнить игру",
"игровая валюта купить",
"донат валюта","донат баланс",

"buy game currency","game top up",
"top up game","game recharge",
"in game currency","virtual currency",

# ===== КОНКРЕТНЫЕ ИГРЫ (ДОНАТ) =====
"donate csgo","csgo skins buy",
"donate dota","dota 2 items",
"valorant points","vp valorant",
"fortnite vbucks","v bucks",
"pubg uc","uc pubg",
"genshin donate","genshin crystals",

# ===== МОБИЛЬНЫЕ ДОНАТЫ =====
"mobile game donate","донат мобилка",
"донат android","донат ios",
"google play donate","appstore donate",

# ===== ОБМЕН / МАРКЕТЫ =====
"игровой маркет","game market",
"trade skins","skin market",
"sell skins","buy skins",

# ===== СЕРЫЕ ВАРИАЦИИ =====
"cheap donate","донат дешево",
"донат скидка","донат акции",

# ===== РУ ОБЩЕЕ =====
"задонатить","донатить",
"оплата доната","сервис донатов",
"сайт донатов","донат площадка",

# ===== ОШИБКИ =====
"donatovv","donatof","funpaay",
"ggsell","plati rru","donatep ay"

], "Развлечения")


# =========================
# 💳 КРЕДИТЫ 
# =========================
add([

# ===== БАЗА =====
"кредит","кредиты","loan","loans",
"займ","займы","microloan","micro loan",
"ипотека","mortgage",
"рассрочка","installment","bnpl",
"кредитка","credit card","кредитная карта"

# ===== ДЕЙСТВИЯ =====
"оформить кредит","взять кредит",
"получить кредит","заявка на кредит",
"одобрение кредита","онлайн кредит",

"взять займ","получить займ",
"заявка займ","займ онлайн",

"рассрочка оплата","оплата частями",
"buy now pay later",

# ===== ПРОСРОЧКИ / ДОЛГИ =====
"просрочка","просроченный платеж",
"долг","задолженность",
"не плачу кредит","нечем платить",
"штраф по кредиту","penalty loan",
"overdue payment",

# ===== БАНКИ РФ =====
"сбербанк","sberbank","sber",
"тинькофф","tinkoff","tinkoff bank",
"альфа банк","alfabank","alpha bank",
"втб","vtb bank",
"газпромбанк","gazprombank",
"открытие","openbank","bank otkritie",
"райффайзен","raiffeisen","raiffeisenbank",
"росбанк","rosbank",
"совкомбанк","sovcombank",
"почта банк","post bank",
"юникредит","unicredit","unicredit bank",

# ===== НЕОБАНКИ / ONLINE =====
"revolut","revolut bank",
"n26","n26 bank",
"wise","wise bank",
"monzo","monzo bank",
"chime","chime bank",

# ===== МФО РФ =====
"займер","zaymer",
"е капуста","ekapusta","e kapusta",
"moneyman","money man",
"webbankir","web bankir",
"lime займ","lime loan",
"vivus","vivus ru",
"turbozaim","turbo zaim",
"быстроденьги","bystrodengi",
"creditplus","credit plus",
"platiza","platiza ru",

# ===== МФО МИР =====
"cashnetusa","cash net usa",
"lendingclub","lending club",
"sofi","sofi loan",
"upstart loan","upstart",
"prosper loan","prosper",

# ===== BNPL / РАССРОЧКА =====
"klarna","klarna payment",
"afterpay","after pay",
"affirm","affirm payment",
"zip pay","zippay",
"paypal credit","paypal pay later",

"долями","dolyami",
"сплит","yandex split","split payment",

# ===== КРЕДИТНЫЕ КАРТЫ =====
"visa credit","mastercard credit",
"кредитка оформить","оформить карту",
"лимит карты","credit limit",
"минимальный платеж","minimum payment",

# ===== ПРОЦЕНТЫ / УСЛОВИЯ =====
"процент по кредиту","interest rate",
"ставка кредит","loan rate",
"переплата","overpayment",
"график платежей","payment schedule",

# ===== КОЛЛЕКТОРЫ =====
"коллекторы","collection agency",
"debt collectors","collector call",

# ===== РЕФИНАНС =====
"рефинансирование","refinance loan",
"перекредитование",

# ===== КРЕДИТНАЯ ИСТОРИЯ =====
"кредитная история","credit history",
"скоринг","credit score",
"плохая кредитная история","bad credit",

# ===== ОБЩЕЕ =====
"финансы","finance loan",
"деньги в долг","borrow money",
"быстрые деньги","fast money",
"cash loan","instant loan",

# ===== ОШИБКИ =====
"creditt","loaan","zaimmm",
"sberbannk","tinkof","alfabnk",
"vtbb","gazprommbank",

# ===== GENERIC =====
"borrow cash","get loan",
"loan application","apply loan",
"quick loan","urgent loan"

# ===== ПРОДУКТЫ БАНКОВ =====
"потребительский кредит","consumer loan",
"кредит наличными","cash loan",
"кредит онлайн на карту",
"кредит без справок","loan no income proof",
"кредит без отказа","guaranteed loan",

"ипотека новостройка","ипотека вторичка",
"refinance mortgage","mortgage refinance",

"автокредит","car loan","auto loan",
"кредит на авто","car financing",

# ===== КРЕДИТКИ ГЛУБЖЕ =====
"льготный период","grace period",
"без процентов","0% credit",
"кредитка без процентов",
"обслуживание карты","card maintenance fee",

"снятие наличных кредитка","cash advance",
"комиссия за снятие","cash withdrawal fee",

# ===== ПЛАТЕЖИ / СПИСАНИЯ =====
"платеж по кредиту","loan payment",
"ежемесячный платеж","monthly payment",
"автоплатеж кредит","auto payment loan",
"списание кредита","loan charge",

"bank charge loan","loan fee",
"processing fee","loan processing",

# ===== ПРОСРОЧКИ ГЛУБЖЕ =====
"пени","late fee","late payment fee",
"неустойка","penalty fee",
"default loan","loan default",

"просрочка по займу",
"долг по кредитке",
"overdue loan payment",

# ===== ДОЛГИ / ВЗЫСКАНИЕ =====
"взыскание долга","debt recovery",
"исполнительное производство",
"суд по кредиту","court debt",

"арест счета","account freeze",
"block account debt",

# ===== КОЛЛЕКТОРЫ ГЛУБЖЕ =====
"звонят коллекторы",
"передан в коллекторы",
"collection call","debt collection",

# ===== РЕФИНАНС ГЛУБЖЕ =====
"рефинансировать кредит",
"объединение кредитов","debt consolidation",
"consolidation loan",

# ===== КРЕДИТНАЯ ИСТОРИЯ ГЛУБЖЕ =====
"проверка кредитной истории",
"исправить кредитную историю",
"credit bureau","credit report",

"низкий скоринг","low credit score",
"улучшить скоринг","improve credit score",

# ===== ФИНТЕХ / РАССРОЧКА =====
"pay later","pay in 4",
"installments payment",
"split purchase","split bill",

"рассрочка онлайн магазин",
"оплата частями онлайн",

# ===== СЕРВИСЫ ПРОВЕРОК =====
"нбки","nbki credit",
"эквифакс","equifax",
"окб кредит","okb credit bureau",

# ===== ПОДОЗРИТЕЛЬНЫЕ СИГНАЛЫ =====
"быстрый займ без проверки",
"loan no check","instant approval loan",
"деньги сразу","money instantly",

"займ срочно","urgent microloan",
"кредит срочно","urgent credit",

# ===== МФО ПОВЕДЕНИЕ =====
"продление займа","loan extension",
"пролонгация займа","extend loan",

"частичное погашение","partial repayment",
"закрыть займ","close loan",

# ===== ПРОЦЕНТЫ / ЭКОНОМИКА =====
"годовая ставка","apr loan",
"annual percentage rate",
"effective rate","effective interest",

"переплата по кредиту",
"total loan cost",

# ===== МЕЖДУНАРОДНЫЕ ТЕРМИНЫ =====
"personal loan","installment loan",
"short term loan","long term loan",

"secured loan","unsecured loan",
"collateral loan",

# ===== БИЗНЕС КРЕДИТЫ =====
"кредит для бизнеса","business loan",
"sme loan","small business loan",

"оборотный кредит","working capital loan",

# ===== PAYMENTS PATTERNS (ВАЖНО) =====
"loan repayment","repay loan",
"credit repayment","repayment schedule",

"bank installment","installment charge",

# ===== ОШИБКИ ДОБИВКА =====
"microloann","refinanse","creditt cardd",
"loan paymant","overdu loan",

# ===== GENERIC SMART =====
"borrow funds","need money",
"financial help loan",
"quick cash now","instant cash"

], "Кредиты")

def generate_variations():
    extra = []

    def ru_to_en(s):
        table = str.maketrans({
            "а":"a","в":"b","е":"e","к":"k","м":"m","н":"h",
            "о":"o","р":"p","с":"c","т":"t","у":"y","х":"x"
        })
        return s.translate(table)

    def en_to_ru(s):
        table = str.maketrans({
            "a":"а","b":"в","e":"е","k":"к","m":"м","h":"н",
            "o":"о","p":"р","c":"с","t":"т","y":"у","x":"х"
        })
        return s.translate(table)

    for word, category in CATEGORIES_DB:
        w = word.lower()

        # ===== РЕГИСТРЫ =====
        extra.append((w.upper(), category))
        extra.append((w.capitalize(), category))

        # ===== ПРОБЕЛЫ =====
        extra.append((w.replace(" ", ""), category))
        extra.append((w.replace(" ", "-"), category))
        extra.append((w.replace(" ", "_"), category))

        # двойные пробелы
        extra.append((w.replace(" ", "  "), category))

        # ===== СИМВОЛЫ =====
        clean = w.replace(".", "").replace(",", "")
        extra.append((clean, category))

        # ===== ДОМЕНЫ =====
        if " " not in w:
            extra.append((w + ".ru", category))
            extra.append((w + ".com", category))

        # ===== RU ↔ EN МИКС =====
        extra.append((ru_to_en(w), category))
        extra.append((en_to_ru(w), category))

        # ===== LEET =====
        extra.append((w.replace("o", "0"), category))
        extra.append((w.replace("e", "3"), category))
        extra.append((w.replace("a", "@"), category))

        # ===== ЧАСТИЧНЫЕ (ВАЖНО ДЛЯ ПЛАТЕЖЕЙ) =====
        if len(w) > 6:
            extra.append((w[:5], category))
            extra.append((w[:6], category))

    CATEGORIES_DB.extend(extra)


generate_variations()