# GTFS Static API Endpoint
```bash
GET https://api.data.gov.my/gtfs-static/<agency>
```

## What does GTFS Static do?
The GTFS Static API provides access to standardized public transportation schedules and geographic information, following the General Transit Feed Specification (GTFS). To learn more about GTFS and its specifications, you can visit the [GTFS documentation](https://developers.google.com/transit/gtfs) provided by Google.

## Source of GTFS Static Data
The GTFS Static API incorporates data from various transport operators across Malaysia. We currently feature static feeds from the following:
* [KTMB (Keretapi Tanah Melayu Berhad)](https://www.ktmb.com.my/): A railway operator providing train services across the country.
* [Prasarana](https://www.myrapid.com.my/): A public transport operator responsible for managing various modes of transportation, including LRT (Light Rail Transit), MRT (Mass Rapid Transit), monorail, and bus services.
* [BAS.MY](https://www.mybas.my/): Stage bus services across Malaysia, run by various operators. Endpoints for Kangar, Alor Setar, Kota Bharu, Terengganu, Ipoh, Seremban, Melaka, Johor Bahru, and Kuching are currently available.

## Frequency of Data Update
* GTFS for KTMB: Daily at 00:01:00.
* GTFS for Prasarana: As required.
* GTFS for all BAS.MY services: As required.

If you are scheduling a cron job, we recommend refreshing the static data at least once per day at 4am, i.e. right before rail and bus services nationwide begin their daily operations.

# Request Query & Response Format
The GTFS Static API provides access to public transportation data represented as a GTFS Feed, which consists of a collection of text files packaged in a **ZIP file**. You can access these data files through the following endpoints:

## KTMB
```bash
GET https://api.data.gov.my/gtfs-static/ktmb
# ZIP file is returned
```

## Prasarana
```bash
GET https://api.data.gov.my/gtfs-static/prasarana?category=<category>
# ZIP file is returned
```

* The possible `<category>` values are `rapid-bus-penang`, `rapid-bus-kuantan`, `rapid-bus-mrtfeeder`, `rapid-rail-kl` and `rapid-bus-kl`.
* Note: A small number of trips (~2%, fully specified in [this CSV](https://openapi-malaysia-transport.s3.ap-southeast-1.amazonaws.com/prasarana/problematic_trips.csv)) for the `rapid-bus-kl` endpoint have been removed from the `stop_times.txt` file due to operational issues which affect data accuracy. We are actively working to resolve and restore them to our GTFS feed.

## BAS.MY Kangar
```bash
GET https://api.data.gov.my/gtfs-static/mybas-kangar
# ZIP file is returned
```

## BAS.MY Alor Setar
```bash
GET https://api.data.gov.my/gtfs-static/mybas-alor-setar
# ZIP file is returned
```

## BAS.MY Kota Bharu
```bash
GET https://api.data.gov.my/gtfs-static/mybas-kota-bharu
# ZIP file is returned
```

## BAS.MY Kuala Terengganu
```bash
GET https://api.data.gov.my/gtfs-static/mybas-kuala-terengganu
# ZIP file is returned
```

## BAS.MY Ipoh
```bash
GET https://api.data.gov.my/gtfs-static/mybas-ipoh
# ZIP file is returned
```

## BAS.MY Seremban
Unlike for BAS.MY services in other states, there are 2 endpoints for Seremban, due to the presence of 2 operators which separately provide data to for dissemination via the national Open API. Users should query both endpoints to get a complete picture of currently-running BAS.MY services in Seremban.
```bash
GET https://api.data.gov.my/gtfs-static/mybas-seremban-a
# ZIP file is returned
```

```bash
GET https://api.data.gov.my/gtfs-static/mybas-seremban-b
# ZIP file is returned
```

## BAS.MY Melaka
```bash
GET https://api.data.gov.my/gtfs-static/mybas-melaka
# ZIP file is returned
```

## BAS.MY Johor Bahru
```bash
GET https://api.data.gov.my/gtfs-static/mybas-johor
# ZIP file is returned
```

## BAS.MY Kuching
```bash
GET https://api.data.gov.my/gtfs-static/mybas-kuching
# ZIP file is returned
```

## Understanding the data
Upon extracting the ZIP files obtained from the API endpoints, you will find various text files. Here are the essential text files provided by all agencies:

| GTFS Type | Description |
| :--- | :--- |
| `agency.txt` | Information about transit agencies |
| `stops.txt` | Information about transit stops |
| `routes.txt` | Details about transit routes |
| `trips.txt` | Specific trips with associated route information |
| `stop_times.txt` | Timetables and stop details for trips |
| `calendar.txt` | Service availability for specific dates |

Other optional files, such as `frequencies.txt` and `shapes.txt`, are provided if available. For more details, refer to the [GTFS Schedule Reference](https://gtfs.org/schedule/reference/).

