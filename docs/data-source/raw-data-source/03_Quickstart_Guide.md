# Before you start
The Open API does not require an API token. To ensure responsible usage and prevent abuse, there are limits on the number of requests users can make.

# Sending a Request
To access the Open API, always use the base URL https://api.data.gov.my to send a HTTP GET request. When making API requests, prepend this base URL to the specific API endpoints you want to access. Here's an example of a request that returns a maximum of 3 fuel price records, using the [Data Catalogue API]():

```bash
GET https://api.data.gov.my/data-catalogue?id=fuelprice&limit=3
```

In this example:

* The base URL is https://api.data.gov.my.
* The specific API endpoint is /catalogue.
* The query parameters used are id and limit.

# Postman Collection
We recommend starting your exploration of the Open API by interacting with our Postman collection. The collection provides an interactive environment where you can send requests and receive real-time responses. It offers comprehensive examples of all available endpoints, allowing you to experiment, replicate requests, and customize them to meet your specific needs.